"use client";

import { FormEvent, useState, useEffect } from "react";

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
}

interface TaskFormProps {
  mode: "create" | "edit";
  initialTask?: Task;
  onSubmit: (title: string, description: string) => Promise<void>;
  onCancel?: () => void;
  error?: string;
}

export default function TaskForm({ mode, initialTask, onSubmit, onCancel, error }: TaskFormProps) {
  const [title, setTitle] = useState(initialTask?.title || "");
  const [description, setDescription] = useState(initialTask?.description || "");
  const [isLoading, setIsLoading] = useState(false);
  const [validationError, setValidationError] = useState("");

  useEffect(() => {
    if (initialTask) {
      setTitle(initialTask.title);
      setDescription(initialTask.description || "");
    }
  }, [initialTask]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setValidationError("");

    if (!title.trim()) {
      setValidationError("Title is required");
      return;
    }

    setIsLoading(true);
    try {
      await onSubmit(title.trim(), description.trim());
      if (mode === "create") {
        setTitle("");
        setDescription("");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const displayError = validationError || error;

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-md">
      <h2 className="text-xl font-semibold text-slate-900 mb-5">
        {mode === "create" ? "Create New Task" : "Edit Task"}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-5">
        {displayError && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {displayError}
          </div>
        )}

        <div>
          <label htmlFor="title" className="block text-sm font-medium text-slate-700 mb-2">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2.5 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder:text-slate-400 transition-colors duration-200"
            placeholder="Enter task title"
            disabled={isLoading}
            required
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-slate-700 mb-2">
            Description <span className="text-slate-400 text-xs">(optional)</span>
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            className="w-full px-3 py-2.5 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder:text-slate-400 resize-none transition-colors duration-200"
            placeholder="Add more details about this task"
            disabled={isLoading}
          />
        </div>

        <div className="flex items-center gap-3 pt-1">
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2.5 bg-indigo-600 text-white font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed transition-colors duration-200 shadow-sm"
          >
            {isLoading ? "Saving..." : mode === "create" ? "Create Task" : "Save Changes"}
          </button>

          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              disabled={isLoading}
              className="px-4 py-2.5 bg-slate-100 text-slate-700 font-medium rounded-md hover:bg-slate-200 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 transition-colors duration-200"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
