"use client";

import { useState } from "react";

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
}

interface TaskItemProps {
  task: Task;
  onToggleComplete: (id: string) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => Promise<void>;
}

export default function TaskItem({ task, onToggleComplete, onEdit, onDelete }: TaskItemProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

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
      setShowConfirm(false);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm hover:shadow-md transition-all duration-200">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 mt-1">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={handleToggle}
            disabled={isToggling}
            className="w-5 h-5 rounded border-slate-300 text-indigo-600 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 cursor-pointer disabled:cursor-not-allowed transition-colors duration-200"
          />
        </div>

        <div className="flex-grow min-w-0">
          <h3
            className={`text-lg font-semibold ${
              task.completed ? "line-through text-slate-500" : "text-slate-900"
            }`}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              className={`mt-1 text-sm ${
                task.completed ? "line-through text-slate-400" : "text-slate-600"
              }`}
            >
              {task.description}
            </p>
          )}
        </div>

        <div className="flex-shrink-0 flex items-center gap-2">
          <button
            onClick={() => onEdit(task)}
            className="px-3 py-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded-md transition-colors duration-200"
            disabled={isDeleting}
          >
            Edit
          </button>

          {!showConfirm ? (
            <button
              onClick={() => setShowConfirm(true)}
              className="px-3 py-1.5 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors duration-200"
              disabled={isDeleting}
            >
              Delete
            </button>
          ) : (
            <div className="flex items-center gap-1.5">
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-3 py-1.5 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md disabled:opacity-60 transition-colors duration-200"
              >
                {isDeleting ? "..." : "Confirm"}
              </button>
              <button
                onClick={() => setShowConfirm(false)}
                disabled={isDeleting}
                className="px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-md transition-colors duration-200"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
