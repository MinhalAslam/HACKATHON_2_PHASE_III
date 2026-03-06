"use client";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  isNew?: boolean;
}

export default function ChatBubble({ role, content, timestamp, isNew = false }: ChatBubbleProps) {
  const isUser = role === "user";

  return (
    <div
      className={`
        flex ${isUser ? "justify-end" : "justify-start"} mb-4
        ${isNew ? "animate-slide-up" : ""}
      `}
    >
      {/* Avatar for assistant */}
      {!isUser && (
        <div className="flex-shrink-0 mr-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-md">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
      )}

      <div className={`max-w-[75%] ${isUser ? "order-1" : ""}`}>
        <div
          className={`
            relative px-4 py-3 rounded-2xl shadow-sm
            transition-all duration-200
            ${isUser
              ? "bg-gradient-to-br from-indigo-500 to-indigo-600 text-white rounded-br-md"
              : "bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700 rounded-bl-md"
            }
          `}
        >
          <p className="text-sm whitespace-pre-wrap break-words leading-relaxed">{content}</p>
        </div>

        {timestamp && (
          <p
            className={`
              text-xs mt-1.5 px-1
              ${isUser ? "text-right text-slate-500" : "text-slate-400 dark:text-slate-500"}
            `}
          >
            {new Date(timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
        )}
      </div>

      {/* Avatar for user */}
      {isUser && (
        <div className="flex-shrink-0 ml-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center shadow-md">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
        </div>
      )}
    </div>
  );
}
