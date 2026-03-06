"use client";

import { useState, useEffect } from "react";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";
import { apiClient, getCurrentUserId } from "@/lib/api-client";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at?: string;
}

interface ChatContainerProps {
  initialConversationId?: string;
}

export default function ChatContainer({ initialConversationId }: ChatContainerProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(
    initialConversationId || null
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState(!!initialConversationId);

  // Load existing conversation on mount if conversationId is provided
  useEffect(() => {
    if (initialConversationId) {
      loadConversation(initialConversationId);
    }
  }, [initialConversationId]);

  const loadConversation = async (convId: string) => {
    try {
      setIsInitializing(true);
      setError(null);
      const data = await apiClient.getConversation(convId);
      setMessages(
        data.messages.map((msg: any) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          created_at: msg.created_at,
        }))
      );
      setConversationId(convId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load conversation");
    } finally {
      setIsInitializing(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    const userId = getCurrentUserId();
    if (!userId) {
      setError("Please login to continue");
      return;
    }

    // Add user message optimistically with a temporary ID
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.sendMessage(content, conversationId || undefined);

      // Update conversation ID if this was the first message
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Replace temp user message and add assistant response
      setMessages((prev) => {
        // Remove the temp message
        const withoutTemp = prev.filter((m) => m.id !== tempUserMessage.id);
        // Add the real user message (reconstructed) and assistant response
        return [
          ...withoutTemp,
          {
            id: `user-${Date.now()}`,
            role: "user" as const,
            content,
            created_at: new Date().toISOString(),
          },
          {
            id: response.message.id,
            role: response.message.role,
            content: response.message.content,
            created_at: response.message.created_at,
          },
        ];
      });
    } catch (err) {
      // Remove the optimistic message on error
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id));
      setError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setIsLoading(false);
    }
  };

  if (isInitializing) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-slate-500">Loading conversation...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {error && (
        <div className="px-4 py-2 bg-red-50 border-b border-red-200 text-red-700 text-sm">
          {error}
          <button
            onClick={() => setError(null)}
            className="ml-2 text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      )}
      <MessageList messages={messages} isLoading={isLoading} />
      <MessageInput
        onSubmit={handleSendMessage}
        disabled={isLoading}
        placeholder="Ask me to manage your tasks..."
      />
    </div>
  );
}
