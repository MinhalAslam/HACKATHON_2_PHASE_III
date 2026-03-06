// API Contracts: Frontend Web Application & API Integration

// TypeScript interfaces for frontend-backend data contracts

export interface User {
  id: string;
  email: string;
  role: string;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterResponse {
  user: User;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskData {
  title: string;
  description?: string;
}

export interface UpdateTaskData {
  title?: string;
  description?: string;
  completed?: boolean;
}

export interface ToggleCompletionData {
  completed: boolean;
}

export interface ApiResponse<T = any> {
  data?: T;
  status: number;
  statusText: string;
  headers?: Record<string, string>;
  error?: {
    message: string;
    details?: any;
  };
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}

// API client interface defining contract
export interface ApiClient {
  // Authentication methods
  login(credentials: LoginCredentials): Promise<ApiResponse<LoginResponse>>;
  register(credentials: RegisterCredentials): Promise<ApiResponse<RegisterResponse>>;
  logout(): Promise<void>;
  getProfile(): Promise<ApiResponse<User>>;

  // Task methods
  getTasks(userId: string): Promise<ApiResponse<Task[]>>;
  createTask(userId: string, taskData: CreateTaskData): Promise<ApiResponse<Task>>;
  getTask(userId: string, taskId: string): Promise<ApiResponse<Task>>;
  updateTask(userId: string, taskId: string, taskData: UpdateTaskData): Promise<ApiResponse<Task>>;
  deleteTask(userId: string, taskId: string): Promise<ApiResponse<void>>;
  toggleTaskCompletion(userId: string, taskId: string, completed: boolean): Promise<ApiResponse<Task>>;

  // Configuration
  setAuthToken(token: string): void;
  clearAuthToken(): void;
}

// Expected error responses
export interface ApiErrorResponse {
  detail: string; // Standard error message format
}

// Success responses by endpoint
export interface TaskListResponse {
  tasks: Task[];
}

export interface TaskDetailResponse {
  task: Task;
}

export interface TaskCreateResponse {
  task: Task;
}

export interface TaskUpdateResponse {
  task: Task;
}

export interface TaskDeleteResponse {
  message: string; // e.g. "Task deleted successfully"
}

// Route protection types
export interface ProtectedRouteProps {
  children: React.ReactNode;
  fallbackUrl?: string; // Redirect path when not authenticated
}

// Authentication context types
export interface AuthContextType {
  state: AuthState;
  login(credentials: LoginCredentials): Promise<boolean>;
  logout(): Promise<void>;
  register(credentials: RegisterCredentials): Promise<boolean>;
}