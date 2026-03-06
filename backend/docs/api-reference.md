# Todo API Reference

## Authentication Endpoints

### Register a new user
```
POST /api/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
- `200 OK`: User successfully registered
- `400 Bad Request`: Email already exists or invalid input

### Login user
```
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
- `200 OK`: Login successful, returns access token
- `401 Unauthorized`: Invalid credentials

### Get current user profile
```
GET /api/auth/me
```
Requires valid JWT token in Authorization header.

**Response:**
- `200 OK`: Returns user profile data
- `401 Unauthorized`: Invalid or expired token

## Task Endpoints

All task endpoints require a valid JWT token and follow the pattern: `/api/{user_id}/tasks`

### Get all tasks for a user
```
GET /api/{user_id}/tasks
```

**Response:**
- `200 OK`: Returns list of tasks
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User ID doesn't match token

### Create a new task
```
POST /api/{user_id}/tasks
```

**Request Body:**
```json
{
  "title": "New task title",
  "description": "Task description (optional)"
}
```

**Response:**
- `201 Created`: Task created successfully
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User ID doesn't match token

### Get a specific task
```
GET /api/{user_id}/tasks/{task_id}
```

**Response:**
- `200 OK`: Returns task details
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User ID doesn't match token or task doesn't belong to user
- `404 Not Found`: Task not found

### Update a task
```
PUT /api/{user_id}/tasks/{task_id}
```

**Request Body:**
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "completed": false
}
```

**Response:**
- `200 OK`: Task updated successfully
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User ID doesn't match token or task doesn't belong to user
- `404 Not Found`: Task not found

### Delete a task
```
DELETE /api/{user_id}/tasks/{task_id}
```

**Response:**
- `200 OK`: Task deleted successfully
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User ID doesn't match token or task doesn't belong to user
- `404 Not Found`: Task not found

### Toggle task completion status
```
PATCH /api/{user_id}/tasks/{task_id}/complete
```

**Request Body:**
```json
{
  "completed": true
}
```

**Response:**
- `200 OK`: Task completion status updated
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User ID doesn't match token or task doesn't belong to user
- `404 Not Found`: Task not found

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message"
}
```