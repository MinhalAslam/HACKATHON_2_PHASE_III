"""
Chat Router for AI Chatbot.

Provides endpoints for chat conversations and message handling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from ..database.database import get_session
from ..models.conversation import ConversationRead, ConversationSummary
from ..models.message import MessageRead, MessageRole
from ..services.chat_service import ChatService
from ..agent.task_agent import run_agent
from ..utils.auth import get_current_user_id, verify_url_user_id_matches_token

router = APIRouter()


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    message: str
    conversation_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""
    conversation_id: UUID
    message: MessageRead


class ConversationWithMessages(BaseModel):
    """Response body for getting a conversation with its messages."""
    conversation: ConversationRead
    messages: List[MessageRead]


@router.post("/chat", response_model=ChatResponse)
def send_chat_message(
    user_id: str,
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Send a chat message and get an AI response.

    Creates a new conversation if conversation_id is not provided.
    Stores both user message and assistant response in the database.
    """
    # Verify URL user_id matches token
    verify_url_user_id_matches_token(user_id, current_user_id)
    user_uuid = UUID(user_id)

    chat_service = ChatService(session)

    # Get or create conversation
    if request.conversation_id:
        conversation = chat_service.get_conversation(request.conversation_id, user_uuid)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation with auto-generated title
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        conversation = chat_service.create_conversation(user_uuid, title=title)

    # Store user message
    chat_service.add_message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=request.message
    )

    # Get conversation history for agent context
    messages = chat_service.get_conversation_for_messages(conversation.id, user_uuid) or []

    # Run agent to get response
    try:
        agent_response = run_agent(messages, user_id)
    except Exception as e:
        agent_response = "I apologize, but I encountered an error processing your request. Please try again."

    # Store assistant response
    assistant_message = chat_service.add_message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=agent_response
    )

    return ChatResponse(
        conversation_id=conversation.id,
        message=MessageRead(
            id=assistant_message.id,
            role=assistant_message.role,
            content=assistant_message.content,
            conversation_id=assistant_message.conversation_id,
            created_at=assistant_message.created_at
        )
    )


@router.get("/conversations", response_model=List[ConversationSummary])
def list_conversations(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    List all conversations for the authenticated user.

    Returns conversations ordered by most recent activity.
    """
    verify_url_user_id_matches_token(user_id, current_user_id)
    user_uuid = UUID(user_id)

    chat_service = ChatService(session)
    return chat_service.list_conversations(user_uuid)


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
def get_conversation(
    user_id: str,
    conversation_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Get a specific conversation with all its messages.

    Returns 404 if conversation not found or not owned by user.
    """
    verify_url_user_id_matches_token(user_id, current_user_id)
    user_uuid = UUID(user_id)

    chat_service = ChatService(session)
    conversation = chat_service.get_conversation(conversation_id, user_uuid)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    messages = chat_service.get_messages(conversation_id)

    return ConversationWithMessages(
        conversation=ConversationRead(
            id=conversation.id,
            title=conversation.title,
            user_id=conversation.user_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        ),
        messages=[
            MessageRead(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                conversation_id=msg.conversation_id,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    user_id: str,
    conversation_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Delete a conversation and all its messages.

    Returns 404 if conversation not found or not owned by user.
    """
    verify_url_user_id_matches_token(user_id, current_user_id)
    user_uuid = UUID(user_id)

    chat_service = ChatService(session)
    deleted = chat_service.delete_conversation(conversation_id, user_uuid)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return None
