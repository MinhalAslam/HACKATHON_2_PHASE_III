"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import ChatBubble from "@/components/chat/ChatBubble";
import ChatInput from "@/components/chat/ChatInput";
import TypingIndicator from "@/components/chat/TypingIndicator";
import { apiClient, getCurrentUserId, isAuthenticated } from "@/lib/api-client";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at?: string;
  isNew?: boolean;
}

interface Conversation {
  id: string;
  title: string;
  updated_at: string;
}

function ChatPageContent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const searchParams = useSearchParams();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    loadConversations();

    const convId = searchParams.get("conversation");
    if (convId) {
      loadConversation(convId);
    }
  }, [router, searchParams]);

  const loadConversations = async () => {
    try {
      setIsLoadingConversations(true);
      const data = await apiClient.getConversations();
      setConversations(data);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const loadConversation = async (convId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiClient.getConversation(convId);
      setMessages(
        data.messages.map((msg: any) => ({
          id: msg.id,
          role: msg.role.toLowerCase(),
          content: msg.content,
          created_at: msg.created_at,
        }))
      );
      setConversationId(convId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load conversation");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    const userId = getCurrentUserId();
    if (!userId) {
      setError("Please login to continue");
      return;
    }

    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content,
      created_at: new Date().toISOString(),
      isNew: true,
    };
    setMessages((prev) => [...prev, tempUserMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.sendMessage(content, conversationId || undefined);

      if (!conversationId) {
        setConversationId(response.conversation_id);
        loadConversations(); // Refresh sidebar
      }

      setMessages((prev) => {
        const withoutTemp = prev.filter((m) => m.id !== tempUserMessage.id);
        return [
          ...withoutTemp,
          { ...tempUserMessage, id: `user-${Date.now()}`, isNew: false },
          {
            id: response.message.id,
            role: response.message.role.toLowerCase(),
            content: response.message.content,
            created_at: response.message.created_at,
            isNew: true,
          },
        ];
      });
    } catch (err) {
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id));
      setError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    router.push("/chat");
  };

  const handleSelectConversation = (convId: string) => {
    loadConversation(convId);
    router.push(`/chat?conversation=${convId}`);
  };

  return (
    <DashboardLayout>
      <div className="flex h-[calc(100vh-10rem)] gap-6 animate-fade-in">
        {/* Sidebar - Conversation List */}
        <div
          className={`
            ${showSidebar ? "w-80" : "w-0"} flex-shrink-0
            bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700
            overflow-hidden transition-all duration-300
          `}
        >
          <div className="h-full flex flex-col">
            {/* Sidebar Header */}
            <div className="p-4 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Chats</h2>
                <button
                  onClick={handleNewChat}
                  className="p-2 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded-xl transition-colors"
                  title="New chat"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Conversation List */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
              {isLoadingConversations ? (
                <div className="flex items-center justify-center py-8">
                  <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : conversations.length === 0 ? (
                <div className="text-center py-8 px-4">
                  <p className="text-sm text-slate-500 dark:text-slate-400">No conversations yet</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {conversations.map((conv) => (
                    <button
                      key={conv.id}
                      onClick={() => handleSelectConversation(conv.id)}
                      className={`
                        w-full text-left px-4 py-3 rounded-xl transition-all duration-200
                        ${conversationId === conv.id
                          ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400"
                          : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                        }
                      `}
                    >
                      <p className="font-medium truncate text-sm">{conv.title}</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                        {new Date(conv.updated_at).toLocaleDateString()}
                      </p>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Toggle Sidebar Button */}
        <button
          onClick={() => setShowSidebar(!showSidebar)}
          className="absolute left-4 top-1/2 -translate-y-1/2 z-10 p-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm hover:shadow-md transition-all md:hidden"
        >
          <svg
            className={`w-5 h-5 text-slate-600 dark:text-slate-400 transition-transform ${showSidebar ? "rotate-180" : ""}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          {/* Chat Header */}
          <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700 bg-gradient-to-r from-indigo-500 to-purple-600">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Task Assistant</h2>
                <p className="text-sm text-white/70">AI-powered task management</p>
              </div>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center px-6">
                <div className="w-20 h-20 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center mb-4">
                  <svg className="w-10 h-10 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
                  Start a conversation
                </h3>
                <p className="text-slate-500 dark:text-slate-400 mb-8 max-w-md">
                  I can help you manage your tasks. Try asking me to add, update, delete, or list your tasks!
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
                  {[
                    "Add a task to buy groceries",
                    "Show all my tasks",
                    "Mark my first task as done",
                    "Delete completed tasks",
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => handleSendMessage(suggestion)}
                      className="px-4 py-3 text-sm text-left text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <ChatBubble
                    key={message.id}
                    role={message.role}
                    content={message.content}
                    timestamp={message.created_at}
                    isNew={message.isNew}
                  />
                ))}
                {isLoading && <TypingIndicator />}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Error Banner */}
          {error && (
            <div className="px-6 py-3 bg-red-50 dark:bg-red-900/30 border-t border-red-200 dark:border-red-800">
              <p className="text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
                <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {error}
                <button onClick={() => setError(null)} className="ml-auto text-red-500 hover:text-red-700">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </p>
            </div>
          )}

          {/* Input Area */}
          <ChatInput
            onSubmit={handleSendMessage}
            disabled={isLoading}
            placeholder="Ask me to manage your tasks..."
          />
        </div>
      </div>
    </DashboardLayout>
  );
}

export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <DashboardLayout>
          <div className="flex items-center justify-center h-[calc(100vh-10rem)]">
            <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        </DashboardLayout>
      }
    >
      <ChatPageContent />
    </Suspense>
  );
}
