"use client";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export default function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-500 text-white rounded-br-md"
            : "bg-slate-100 text-slate-900 rounded-bl-md"
        }`}
      >
        <p className="text-sm whitespace-pre-wrap break-words">{content}</p>
        {timestamp && (
          <p
            className={`text-xs mt-1 ${
              isUser ? "text-blue-100" : "text-slate-400"
            }`}
          >
            {new Date(timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
        )}
      </div>
    </div>
  );
}
