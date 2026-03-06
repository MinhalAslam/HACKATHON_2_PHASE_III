"use client";

import { useState } from "react";

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority?: "low" | "medium" | "high";
}

interface TaskCardProps {
  task: Task;
  index: number;
  onToggleComplete: (id: string) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => Promise<void>;
}

export default function TaskCard({ task, index, onToggleComplete, onEdit, onDelete }: TaskCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [showActions, setShowActions] = useState(false);

  const handleToggle = async () => {
    setIsToggling(true);
    try {
      await onToggleComplete(task.id);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(task.id);
    } finally {
      setIsDeleting(false);
    }
  };

  const priorityColors = {
    low: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
    medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    high: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  };

  const priorityDots = {
    low: "bg-emerald-500",
    medium: "bg-amber-500",
    high: "bg-red-500",
  };

  return (
    <div
      className={`
        group relative bg-white dark:bg-slate-800 rounded-2xl p-5
        border border-slate-200 dark:border-slate-700
        shadow-sm hover:shadow-md dark:shadow-slate-900/20
        transition-all duration-300 ease-out
        hover:scale-[1.01] hover:-translate-y-0.5
        animate-slide-up opacity-0
        ${task.completed ? "opacity-70" : ""}
      `}
      style={{ animationDelay: `${index * 0.05}s`, animationFillMode: "forwards" }}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Priority indicator */}
      {task.priority && (
        <div className={`absolute top-0 left-6 w-8 h-1 rounded-b-full ${priorityDots[task.priority]}`} />
      )}

      <div className="flex items-start gap-4">
        {/* Custom checkbox */}
        <button
          onClick={handleToggle}
          disabled={isToggling}
          className={`
            relative flex-shrink-0 w-6 h-6 mt-0.5 rounded-full border-2
            transition-all duration-200 ease-out
            ${task.completed
              ? "bg-indigo-500 border-indigo-500"
              : "border-slate-300 dark:border-slate-600 hover:border-indigo-400"
            }
            ${isToggling ? "animate-pulse-soft" : ""}
            focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
          `}
        >
          {task.completed && (
            <svg
              className="absolute inset-0 w-6 h-6 text-white p-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>

        {/* Task content */}
        <div className="flex-grow min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3
              className={`
                text-base font-semibold transition-all duration-200
                ${task.completed
                  ? "line-through text-slate-400 dark:text-slate-500"
                  : "text-slate-900 dark:text-slate-100"
                }
              `}
            >
              {task.title}
            </h3>
            {task.priority && (
              <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${priorityColors[task.priority]}`}>
                {task.priority}
              </span>
            )}
          </div>

          {task.description && (
            <p
              className={`
                text-sm transition-all duration-200
                ${task.completed
                  ? "line-through text-slate-400 dark:text-slate-600"
                  : "text-slate-600 dark:text-slate-400"
                }
              `}
            >
              {task.description}
            </p>
          )}
        </div>

        {/* Action buttons */}
        <div
          className={`
            flex items-center gap-1 transition-all duration-200
            ${showActions ? "opacity-100 translate-x-0" : "opacity-0 translate-x-2"}
          `}
        >
          <button
            onClick={() => onEdit(task)}
            disabled={isDeleting}
            className="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded-xl transition-colors duration-200"
            title="Edit task"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>

          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className={`
              p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30
              rounded-xl transition-colors duration-200
              ${isDeleting ? "animate-pulse-soft" : ""}
            `}
            title="Delete task"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
