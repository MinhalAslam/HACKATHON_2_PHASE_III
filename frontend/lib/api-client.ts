/**
 * Centralized API Client with automatic JWT authentication
 *
 * This client handles:
 * - Automatic JWT token attachment to all requests
 * - 401 Unauthorized detection and redirect to login
 * - Error handling and response parsing
 * - Communication with FastAPI backend
 */

// Use relative URLs so requests go through Next.js rewrite proxy (next.config.ts).
// This avoids CORS issues — the browser always talks to the same origin (localhost:3000),
// and Next.js proxies /api/* to the backend.
// Only use an absolute URL if explicitly set AND running outside the browser (e.g. SSR).
const API_BASE_URL = typeof window !== 'undefined' ? '' : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

/**
 * Get JWT token from localStorage
 * Returns null if no token is found
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  return localStorage.getItem('access_token');
}

/**
 * Store JWT token in localStorage
 */
function setAuthToken(token: string): void {
  if (typeof window === 'undefined') {
    return;
  }
  localStorage.setItem('access_token', token);
}

/**
 * Clear JWT token from localStorage
 */
function clearAuthToken(): void {
  if (typeof window === 'undefined') {
    return;
  }
  localStorage.removeItem('access_token');
}

/**
 * Build headers with JWT token if available
 */
function getAuthHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

/**
 * Handle API response and errors - DEFENSIVE VERSION
 * Automatically redirects to login on 401
 */
async function handleResponse<T>(response: Response): Promise<T> {
  // Handle 401 Unauthorized
  if (response.status === 401) {
    // Try to extract the backend error detail first, before any redirect
    let errorMessage = 'Unauthorized - please login again';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      // Couldn't parse error response - use default message
    }

    // If already on login page, just throw the error (e.g. "Incorrect email or password")
    // instead of redirecting in a loop
    const isOnLoginPage = typeof window !== 'undefined' && window.location.pathname === '/login';
    if (!isOnLoginPage) {
      clearAuthToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
        // Return a never-resolving promise to prevent further execution during redirect
        return new Promise<T>(() => {});
      }
    }

    throw new Error(errorMessage);
  }

  // Handle 403 Forbidden
  if (response.status === 403) {
    throw new Error('Forbidden - you do not have permission to access this resource');
  }

  // Handle 404 Not Found
  if (response.status === 404) {
    throw new Error('Resource not found');
  }

  // Handle 422 Validation Error (FastAPI validation)
  if (response.status === 422) {
    try {
      const errorData = await response.json();
      if (Array.isArray(errorData.detail)) {
        const messages = errorData.detail.map((e: any) => e.msg || e.message).join(', ');
        throw new Error(`Validation error: ${messages}`);
      }
      throw new Error(errorData.detail || 'Validation failed');
    } catch (error) {
      if (error instanceof Error) throw error;
      throw new Error('Validation failed');
    }
  }

  // Handle 500+ Internal Server Error
  if (response.status >= 500) {
    let errorMessage = `Server error (${response.status}) - please try again later`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorData.error || errorMessage;
      // If the error response contains a traceback, include it (but sanitize it)
      if (errorData.traceback) {
        console.error('Server traceback:', errorData.traceback);
      }
    } catch (parseError) {
      // If we can't parse the JSON error response, try getting the raw text
      try {
        const errorText = await response.text();
        console.error('Raw server error response:', errorText);
        if (errorText.toLowerCase().includes('connection') || errorText.toLowerCase().includes('database')) {
          errorMessage = 'Server error: Database connection issue. Check your database configuration.';
        } else if (errorText.toLowerCase().includes('table') || errorText.toLowerCase().includes('relation')) {
          errorMessage = 'Server error: Database tables may not be initialized. Run create_tables.py first.';
        } else if (errorText.toLowerCase().includes('jwt') || errorText.toLowerCase().includes('token')) {
          errorMessage = 'Server error: Authentication token issue. Check JWT configuration.';
        }
      } catch {
        // Use the default message if we can't read the error response
      }
    }
    throw new Error(errorMessage);
  }

  // Handle successful responses (2xx)
  if (response.ok) {
    // 204 No Content (DELETE operations)
    if (response.status === 204) {
      return {} as T;
    }

    // Try to parse JSON response
    try {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      // Handle non-JSON success responses
      const text = await response.text();
      if (!text) {
        return {} as T; // Empty success response
      }
      throw new Error(`Unexpected response format: ${text.substring(0, 100)}`);
    } catch (error) {
      // JSON parsing failed
      if (error instanceof SyntaxError) {
        throw new Error('Invalid JSON response from server');
      }
      throw error;
    }
  }

  // Handle other 4xx client errors (400, etc.)
  let errorMessage = `Request failed: ${response.status} ${response.statusText}`;
  try {
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } else {
      // Non-JSON error response (HTML error page, etc.)
      const text = await response.text();
      if (text && (text.includes('<!DOCTYPE') || text.includes('<html>'))) {
        errorMessage = 'Server returned an error page instead of JSON';
      } else if (text) {
        errorMessage = text.substring(0, 200); // Truncate long text
      }
    }
  } catch {
    // Couldn't parse error response - use default message
  }

  throw new Error(errorMessage);
}

/**
 * API Client for FastAPI backend
 */
export const apiClient = {
  /**
   * Get all tasks for the authenticated user
   */
  async getTasks(userId?: string): Promise<any[]> {
    const effectiveUserId = userId || getUserIdFromToken();
    if (!effectiveUserId) {
      throw new Error('User ID not found. Please login again.');
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/${effectiveUserId}/tasks`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });
      return handleResponse(response);
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error - unable to reach server. Please check your connection.');
      }
      throw error;
    }
  },

  /**
   * Create a new task
   */
  async createTask(title: string, description?: string, userId?: string): Promise<any> {
    const effectiveUserId = userId || getUserIdFromToken();
    if (!effectiveUserId) {
      throw new Error('User ID not found. Please login again.');
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/${effectiveUserId}/tasks`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ title, description }),
      });
      return handleResponse(response);
    } catch (error) {
      // Catch network errors (CORS, connection refused, etc.)
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error - unable to reach server. Please check your connection.');
      }
      throw error;
    }
  },

  /**
   * Get a single task by ID
   */
  async getTask(taskId: string, userId?: string): Promise<any> {
    const effectiveUserId = userId || getUserIdFromToken();
    if (!effectiveUserId) {
      throw new Error('User ID not found. Please login again.');
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/${effectiveUserId}/tasks/${taskId}`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });
      return handleResponse(response);
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error - unable to reach server. Please check your connection.');
      }
      throw error;
    }
  },

  /**
   * Update an existing task
   */
  async updateTask(taskId: string, title: string, description?: string, userId?: string): Promise<any> {
    const effectiveUserId = userId || getUserIdFromToken();
    if (!effectiveUserId) {
      throw new Error('User ID not found. Please login again.');
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/${effectiveUserId}/tasks/${taskId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ title, description }),
      });
      return handleResponse(response);
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error - unable to reach server. Please check your connection.');
      }
      throw error;
    }
  },

  /**
   * Toggle task completion status
   */
  async toggleTaskComplete(taskId: string, userId?: string): Promise<any> {
    const effectiveUserId = userId || getUserIdFromToken();
    if (!effectiveUserId) {
      throw new Error('User ID not found. Please login again.');
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/${effectiveUserId}/tasks/${taskId}/complete`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
      });
      return handleResponse(response);
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error - unable to reach server. Please check your connection.');
      }
      throw error;
    }
  },

  /**
   * Delete a task
   */
  async deleteTask(taskId: string, userId?: string): Promise<void> {
    const effectiveUserId = userId || getUserIdFromToken();
    if (!effectiveUserId) {
      throw new Error('User ID not found. Please login again.');
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/${effectiveUserId}/tasks/${taskId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      return handleResponse(response);
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error - unable to reach server. Please check your connection.');
      }
      throw error;
    }
  },

  /**
   * Login user
   */
  async login(email: string, password: string): Promise<{ access_token: string, token_type: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      // Handle login-specific errors directly (don't use generic handleResponse for login)
      if (response.status === 401) {
        let errorMessage = 'Incorrect email or password';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // Use default message
        }
        throw new Error(errorMessage);
      }

      if (response.status === 422) {
        let errorMessage = 'Invalid email or password format';
        try {
          const errorData = await response.json();
          if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map((e: any) => e.msg || e.message).join(', ');
          } else {
            errorMessage = errorData.detail || errorMessage;
          }
        } catch {
          // Use default message
        }
        throw new Error(errorMessage);
      }

      // Handle 500 Internal Server Error specifically to provide more details
      if (response.status === 500) {
        let errorMessage = 'Internal server error during login. Please check server logs.';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
          // If the error response contains a traceback, include it (but sanitize it)
          if (errorData.traceback) {
            console.error('Server traceback:', errorData.traceback);
          }
        } catch (parseError) {
          // If we can't parse the JSON error response, try getting the raw text
          try {
            const errorText = await response.text();
            console.error('Raw server error response:', errorText);
            if (errorText.toLowerCase().includes('connection') || errorText.toLowerCase().includes('database')) {
              errorMessage = 'Server error: Database connection issue. Check your database configuration.';
            } else if (errorText.toLowerCase().includes('table') || errorText.toLowerCase().includes('relation')) {
              errorMessage = 'Server error: Database tables may not be initialized. Run create_tables.py first.';
            }
          } catch {
            // Use the default message if we can't read the error response
          }
        }
        throw new Error(errorMessage);
      }

      if (!response.ok) {
        let errorMessage = `Login failed: ${response.status} ${response.statusText}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          // Use default message
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();

      // Store the token in localStorage after successful login
      if (result.access_token) {
        setAuthToken(result.access_token);
      }

      return result;
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to reach server. Please ensure the backend is running on http://localhost:8000.');
      }
      throw error;
    }
  },

  /**
   * Register new user
   */
  async register(email: string, password: string): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      const result = await handleResponse(response);

      // The backend register endpoint doesn't return a token by default
      // Only login returns a token. The user needs to login after registration.

      return result;
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to reach server. Please ensure the backend is running.');
      }
      throw error;
    }
  },

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    clearAuthToken();
    const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    // Don't throw error if logout fails - just clear local token
    if (!response.ok) {
      console.warn('Logout request failed, but local token was cleared');
    }
  },

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });
      return handleResponse(response);
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error - unable to reach server. Please check your connection.');
      }
      throw error;
    }
  },

  /**
   * Send a chat message
   */
  async sendMessage(message: string, conversationId?: string): Promise<any> {
    const userId = getUserIdFromToken();
    if (!userId) {
      throw new Error('User ID not found. Please login again.');
    }

    try {
      const payload: { message: string; conversation_id?: string } = { message };
      if (conversationId) {
        payload.conversation_id = conversationId;
      }

      const response = await fetch(`${API_BASE_URL}/api/${userId}/chat`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload),
      });

      return handleResponse(response);
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error - unable to reach server. Please check your connection.');
      }
      throw error;
    }
  },

  /**
   * Get a list of conversations for the user
   */
  async getConversations(): Promise<any[]> {
    const userId = getUserIdFromToken();
    if (!userId) {
      throw new Error('User ID not found. Please login again.');
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/${userId}/conversations`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });

      return handleResponse(response);
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error - unable to reach server. Please check your connection.');
      }
      throw error;
    }
  },

  /**
   * Get a specific conversation with its messages
   */
  async getConversation(conversationId: string): Promise<any> {
    const userId = getUserIdFromToken();
    if (!userId) {
      throw new Error('User ID not found. Please login again.');
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/${userId}/conversations/${conversationId}`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });

      return handleResponse(response);
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error - unable to reach server. Please check your connection.');
      }
      throw error;
    }
  },

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: string): Promise<void> {
    const userId = getUserIdFromToken();
    if (!userId) {
      throw new Error('User ID not found. Please login again.');
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/${userId}/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      return handleResponse(response);
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error - unable to reach server. Please check your connection.');
      }
      throw error;
    }
  },
};

/**
 * Extract user ID from JWT token
 * Returns the user_id from the JWT payload
 */
function getUserIdFromToken(): string | null {
  const token = getAuthToken();
  if (!token) {
    return null;
  }

  try {
    // JWT format: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    // Decode the payload (base64url)
    let payload = parts[1];

    // Add proper padding for base64 decoding
    const padding = '='.repeat((4 - (payload.length % 4)) % 4);
    payload += padding;

    // Properly decode base64url to handle UTF-8 characters
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    const decodedPayload = new TextDecoder().decode(bytes);
    const parsedPayload = JSON.parse(decodedPayload);

    // The backend stores user_id in the "sub" field
    return parsedPayload.sub || null;
  } catch (error) {
    console.error('Failed to decode JWT token:', error);
    return null;
  }
}

/**
 * Helper function to check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null;
}

/**
 * Helper function to get current user ID from JWT
 */
export function getCurrentUserId(): string | null {
  return getUserIdFromToken();
}

/**
 * Helper function to clear authentication and redirect to login
 */
export function logout(): void {
  clearAuthToken();
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}
