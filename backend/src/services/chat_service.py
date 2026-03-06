"""
Chat Service for AI Chatbot.

Handles conversation and message persistence operations.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select

from ..models.conversation import Conversation, ConversationCreate, ConversationSummary
from ..models.message import Message, MessageRole


class ChatService:
    """
    Service layer for chat-related operations.

    Manages conversations and messages in the database.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_conversation(
        self,
        user_id: UUID,
        title: Optional[str] = None
    ) -> Conversation:
        """
        Create a new conversation for a user.

        Args:
            user_id: The ID of the user
            title: Optional title for the conversation

        Returns:
            The created Conversation
        """
        conversation = Conversation(
            user_id=user_id,
            title=title,
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID, verifying user ownership.

        Args:
            conversation_id: The conversation ID
            user_id: The user ID for ownership verification

        Returns:
            The Conversation if found and owned by user, else None
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return self.session.exec(statement).first()

    def list_conversations(self, user_id: UUID) -> List[ConversationSummary]:
        """
        List all conversations for a user with summary info.

        Args:
            user_id: The user ID

        Returns:
            List of ConversationSummary objects
        """
        statement = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc())

        conversations = self.session.exec(statement).all()
        summaries = []

        for conv in conversations:
            # Get message count and last message preview
            msg_statement = select(Message).where(
                Message.conversation_id == conv.id
            ).order_by(Message.created_at.desc())
            messages = self.session.exec(msg_statement).all()

            last_preview = None
            if messages:
                last_msg = messages[0]
                last_preview = last_msg.content[:100] + "..." if len(last_msg.content) > 100 else last_msg.content

            summaries.append(ConversationSummary(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=len(messages),
                last_message_preview=last_preview
            ))

        return summaries

    def add_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation_id: The conversation ID
            role: The message role (user or assistant)
            content: The message content

        Returns:
            The created Message
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.session.add(message)

        # Update conversation's updated_at timestamp
        conversation = self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)

        self.session.commit()
        self.session.refresh(message)
        return message

    def get_messages(
        self,
        conversation_id: UUID,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Get all messages in a conversation, ordered by creation time.

        Args:
            conversation_id: The conversation ID
            limit: Optional limit on number of messages (most recent)

        Returns:
            List of Messages ordered by created_at ascending
        """
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())

        messages = list(self.session.exec(statement).all())

        if limit and len(messages) > limit:
            # Return only the most recent messages
            messages = messages[-limit:]

        return messages

    def delete_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: The conversation ID
            user_id: The user ID for ownership verification

        Returns:
            True if deleted, False if not found
        """
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        self.session.delete(conversation)
        self.session.commit()
        return True

    def get_conversation_for_messages(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> Optional[List[dict]]:
        """
        Get conversation messages formatted for the AI agent.

        Args:
            conversation_id: The conversation ID
            user_id: The user ID for ownership verification

        Returns:
            List of message dicts with 'role' and 'content', or None if not found
        """
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None

        messages = self.get_messages(conversation_id)
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]
