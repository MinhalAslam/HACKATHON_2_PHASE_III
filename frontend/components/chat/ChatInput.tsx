"use client";

import { useState, KeyboardEvent, useRef, useEffect } from "react";

interface ChatInputProps {
  onSubmit: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({
  onSubmit,
  disabled = false,
  placeholder = "Type a message...",
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSubmit = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !disabled) {
      onSubmit(trimmedMessage);
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative p-4 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-700">
      <div className="flex items-end gap-3">
        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={`
              w-full resize-none rounded-2xl border border-slate-300 dark:border-slate-600
              bg-slate-50 dark:bg-slate-800
              px-4 py-3 pr-12 text-sm
              text-slate-900 dark:text-slate-100
              placeholder:text-slate-400 dark:placeholder:text-slate-500
              focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
              disabled:bg-slate-100 dark:disabled:bg-slate-700 disabled:cursor-not-allowed
              transition-all duration-200
            `}
            style={{ minHeight: "48px", maxHeight: "120px" }}
          />
        </div>

        <button
          onClick={handleSubmit}
          disabled={disabled || !message.trim()}
          className={`
            flex-shrink-0 w-12 h-12 rounded-xl
            bg-gradient-to-br from-indigo-500 to-indigo-600
            text-white shadow-md
            hover:from-indigo-600 hover:to-indigo-700 hover:shadow-lg
            focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
            disabled:from-slate-300 disabled:to-slate-400 disabled:shadow-none disabled:cursor-not-allowed
            transform transition-all duration-200
            hover:scale-105 active:scale-95
            disabled:hover:scale-100
          `}
        >
          {disabled ? (
            <svg className="w-5 h-5 mx-auto animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            <svg className="w-5 h-5 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>

      <p className="text-xs text-slate-400 dark:text-slate-500 mt-2 text-center">
        Press Enter to send, Shift + Enter for new line
      </p>
    </div>
  );
}
