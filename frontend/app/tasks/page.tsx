"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/DashboardLayout";
import TaskCard from "@/components/ui/TaskCard";
import FloatingChat from "@/components/chat/FloatingChat";
import Toast, { ToastType } from "@/components/ui/Toast";
import { apiClient, isAuthenticated } from "@/lib/api-client";

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority?: "low" | "medium" | "high";
}

interface ToastItem {
  id: string;
  message: string;
  type: ToastType;
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskDescription, setNewTaskDescription] = useState("");
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [filter, setFilter] = useState<"all" | "pending" | "completed">("all");
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const router = useRouter();

  const addToast = (message: string, type: ToastType) => {
    const id = Date.now().toString();
    setToasts((prev) => [...prev, { id, message, type }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const loadTasks = useCallback(async () => {
    try {
      const data = await apiClient.getTasks();
      setTasks(data);
    } catch (err) {
      addToast("Failed to load tasks", "error");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    loadTasks();
  }, [router, loadTasks]);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;

    try {
      await apiClient.createTask(newTaskTitle, newTaskDescription);
      await loadTasks();
      setNewTaskTitle("");
      setNewTaskDescription("");
      setShowCreateForm(false);
      addToast("Task created successfully", "success");
    } catch (err) {
      addToast("Failed to create task", "error");
    }
  };

  const handleUpdateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTask || !newTaskTitle.trim()) return;

    try {
      await apiClient.updateTask(editingTask.id, newTaskTitle, newTaskDescription);
      await loadTasks();
      setEditingTask(null);
      setNewTaskTitle("");
      setNewTaskDescription("");
      addToast("Task updated successfully", "success");
    } catch (err) {
      addToast("Failed to update task", "error");
    }
  };

  const handleToggleComplete = async (id: string) => {
    try {
      await apiClient.toggleTaskComplete(id);
      await loadTasks();
    } catch (err) {
      addToast("Failed to update task", "error");
    }
  };

  const handleDeleteTask = async (id: string) => {
    try {
      await apiClient.deleteTask(id);
      await loadTasks();
      addToast("Task deleted", "info");
    } catch (err) {
      addToast("Failed to delete task", "error");
    }
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    setNewTaskTitle(task.title);
    setNewTaskDescription(task.description || "");
    setShowCreateForm(false);
  };

  const cancelEdit = () => {
    setEditingTask(null);
    setNewTaskTitle("");
    setNewTaskDescription("");
    setShowCreateForm(false);
  };

  const filteredTasks = tasks.filter((task) => {
    if (filter === "pending") return !task.completed;
    if (filter === "completed") return task.completed;
    return true;
  });

  const completedCount = tasks.filter((t) => t.completed).length;
  const pendingCount = tasks.filter((t) => !t.completed).length;

  return (
    <DashboardLayout>
      <div className="animate-fade-in">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">My Tasks</h1>
            <p className="text-slate-600 dark:text-slate-400 mt-1">
              {tasks.length} total · {pendingCount} pending · {completedCount} completed
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Filter Tabs */}
            <div className="flex items-center bg-slate-100 dark:bg-slate-800 rounded-xl p-1">
              {(["all", "pending", "completed"] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`
                    px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200
                    ${filter === f
                      ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100"
                    }
                  `}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>

            {!showCreateForm && !editingTask && (
              <button
                onClick={() => setShowCreateForm(true)}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-medium rounded-xl hover:from-indigo-600 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span className="hidden sm:inline">New Task</span>
              </button>
            )}
          </div>
        </div>

        {/* Create/Edit Form */}
        {(showCreateForm || editingTask) && (
          <div className="mb-6 animate-slide-up">
            <form
              onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
              className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-sm"
            >
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
                {editingTask ? "Edit Task" : "Create New Task"}
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    value={newTaskTitle}
                    onChange={(e) => setNewTaskTitle(e.target.value)}
                    placeholder="What needs to be done?"
                    className="w-full px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                    autoFocus
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Description (optional)
                  </label>
                  <textarea
                    value={newTaskDescription}
                    onChange={(e) => setNewTaskDescription(e.target.value)}
                    placeholder="Add more details..."
                    rows={3}
                    className="w-full px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none transition-all"
                  />
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <button
                    type="submit"
                    className="px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-medium rounded-xl hover:from-indigo-600 hover:to-purple-700 shadow-md hover:shadow-lg transform hover:scale-105 transition-all duration-200"
                  >
                    {editingTask ? "Update Task" : "Create Task"}
                  </button>
                  <button
                    type="button"
                    onClick={cancelEdit}
                    className="px-5 py-2.5 text-slate-600 dark:text-slate-400 font-medium rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </form>
          </div>
        )}

        {/* Task List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-12 border border-slate-200 dark:border-slate-700 text-center">
            <div className="w-20 h-20 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center mx-auto mb-4">
              <svg className="w-10 h-10 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
              {filter === "all" ? "No tasks yet" : `No ${filter} tasks`}
            </h3>
            <p className="text-slate-500 dark:text-slate-400 mb-6">
              {filter === "all"
                ? "Create your first task or ask the AI assistant!"
                : filter === "pending"
                ? "Great job! All tasks are completed."
                : "Complete some tasks to see them here."}
            </p>
            {filter === "all" && (
              <button
                onClick={() => setShowCreateForm(true)}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-medium rounded-xl hover:from-indigo-600 hover:to-purple-700 shadow-lg transition-all"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create Your First Task
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {filteredTasks.map((task, index) => (
              <TaskCard
                key={task.id}
                task={task}
                index={index}
                onToggleComplete={handleToggleComplete}
                onEdit={handleEdit}
                onDelete={handleDeleteTask}
              />
            ))}
          </div>
        )}
      </div>

      {/* Floating Chat */}
      <FloatingChat onTaskUpdate={loadTasks} />

      {/* Toast Notifications */}
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </DashboardLayout>
  );
}
