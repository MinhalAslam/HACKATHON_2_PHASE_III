# Implementation Plan: Todo Full-Stack Web Application (Hackathon Phase 2)

**Feature**: Todo Full-Stack Web Application (Hackathon Phase 2)
**Created**: 2026-02-05
**Status**: Draft
**Branch**: 1-todo-web-app

## Technical Context

This implementation will transform a single-user, in-memory console Todo application into a secure, multi-user, full-stack web application with persistent storage, RESTful APIs, and JWT-based authentication. The application will use Python FastAPI for the backend, Next.js 16+ with App Router for the frontend, SQLModel for ORM, Neon Serverless PostgreSQL for database, and Better Auth for authentication with JWT tokens.

**Technologies Stack**:
- Frontend: Next.js 16+ with App Router
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (Frontend) + JWT
- Spec-Driven Tools: Claude Code + Spec-Kit Plus only

**Dependencies**:
- Python 3.9+ for backend
- Node.js 18+ for frontend
- Better Auth library for authentication
- PyJWT for JWT handling
- psycopg2-binary for PostgreSQL connection
- SQLModel for database models

## Architecture Overview

The system will follow a microservices-like architecture with clear separation between frontend, backend, and authentication layers:

1. **Frontend Layer** (Next.js 16+):
   - Handles user interface and user experience
   - Manages authentication state using Better Auth
   - Communicates with backend API using JWT tokens in headers
   - Implements responsive design for various screen sizes

2. **Authentication Layer** (Better Auth):
   - Handles user registration and login
   - Issues JWT tokens upon successful authentication
   - Validates credentials and manages user sessions

3. **Backend Layer** (FastAPI + SQLModel):
   - Exposes RESTful API endpoints for task management
   - Validates JWT tokens for all authenticated endpoints
   - Enforces user isolation by checking token identity against URL/user parameters
   - Persists data to Neon PostgreSQL database

4. **Database Layer** (Neon Serverless PostgreSQL):
   - Stores user information and tasks
   - Enforces referential integrity between users and tasks
   - Maintains task ownership and completion states

## Constitution Check

This plan aligns with all constitutional principles:

✅ **Spec-First Development**: Implementation follows the detailed specification created in spec.md
✅ **Security-by-Design**: JWT-based authentication with user isolation enforced at every layer
✅ **Agentic Development Compliance**: Following spec → plan → tasks → implement workflow
✅ **API-First Design**: RESTful API with JWT authentication and proper HTTP methods
✅ **Data Integrity Assurance**: Persistent storage using PostgreSQL, user-scoped data
✅ **Production Realism**: Real database, real auth, clear separation of concerns

## Phase 0: Research & Resolution of Unknowns

### research.md

#### Decision: JWT Verification Approach in FastAPI
- **Chosen**: Using FastAPI dependencies (HTTPBearer) with JWT decoding
- **Rationale**: Provides reusable authentication logic that can be applied to specific endpoints; allows for flexible error handling and validation; integrates well with FastAPI's dependency injection system
- **Alternatives considered**:
  - Middleware approach: More complex for selective endpoint protection
  - Decorator approach: Less flexible and harder to maintain

#### Decision: JWT Claim Structure for User Identity
- **Chosen**: Using 'sub' (subject) claim for user ID and 'exp' for expiration
- **Rationale**: Follows JWT standards; 'sub' is the standard claim for identifying the principal; includes expiration for security
- **Alternatives considered**:
  - Custom claims: Would deviate from standards
  - Multiple claims for identity: Would complicate validation

#### Decision: URL User_ID Matching Strategy
- **Chosen**: Compare authenticated user ID from JWT with user_id path parameter in FastAPI dependencies
- **Rationale**: Provides centralized validation that can be applied consistently across endpoints; allows for clear error responses
- **Alternatives considered**:
  - Manual validation in each endpoint: Repetitive and error-prone
  - Database lookup validation: Unnecessary overhead

#### Decision: Database Schema Design for User-Task Relationship
- **Chosen**: Foreign key relationship between Task and User tables with SQLModel
- **Rationale**: Enforces data integrity at the database level; enables efficient querying with joins; follows relational database best practices
- **Alternatives considered**:
  - Storing user ID as a field without foreign key: No referential integrity
  - Separate tables per user: Complex and doesn't scale

#### Decision: Error Handling and HTTP Status Codes
- **Chosen**: Standard HTTP status codes (200, 201, 401, 403, 404, 500) with descriptive error messages
- **Rationale**: Follows REST API best practices; provides clear communication about request outcomes; compatible with frontend error handling
- **Alternatives considered**:
  - Custom error codes: Non-standard and harder to integrate
  - Generic error responses: Insufficient information for clients

#### Decision: Frontend API Client Structure
- **Chosen**: Centralized API client with automatic JWT token injection
- **Rationale**: Provides single source of truth for API interactions; handles authentication transparently; reduces repetition
- **Alternatives considered**:
  -分散 API calls: Repetitive and harder to maintain
  - Per-component API logic: Inconsistent authentication handling

#### Decision: Environment Variable Management for JWT Secret
- **Chosen**: Using environment variables loaded at application startup
- **Rationale**: Secure way to manage secrets; separates configuration from code; aligns with 12-factor app methodology
- **Alternatives considered**:
  - Hardcoded secrets: Major security risk
  - Configuration files: Potential for accidental commits

## Phase 1: Design & Contracts

### data-model.md

#### User Entity
- **Fields**:
  - id: UUID (primary key)
  - email: String (unique, indexed)
  - created_at: DateTime (timestamp of account creation)
  - updated_at: DateTime (timestamp of last update)
- **Relationships**:
  - Has many Tasks
- **Validation**:
  - Email must be valid format
  - Email must be unique

#### Task Entity
- **Fields**:
  - id: UUID (primary key)
  - title: String (required, max length 200)
  - description: Text (optional)
  - completed: Boolean (default False)
  - user_id: UUID (foreign key to User)
  - created_at: DateTime (timestamp of task creation)
  - updated_at: DateTime (timestamp of last update)
- **Relationships**:
  - Belongs to User
- **Validation**:
  - Title is required
  - user_id must reference an existing user
  - Only the owner can modify the task

#### Database Relationships
- One User to Many Tasks (one-to-many)
- Tasks are linked to Users via foreign key constraint
- Cascading deletes not enabled to preserve user-task relationships

### API Contracts

#### Authentication Endpoints (Handled by Better Auth)
- `/api/auth/signup` (POST) - User registration
- `/api/auth/signin` (POST) - User login
- Both endpoints return JWT tokens upon successful authentication

#### Task Management Endpoints
- `GET /api/{user_id}/tasks`
  - Description: Retrieve all tasks for a specific user
  - Headers: Authorization: Bearer <token>
  - Query Parameters: None
  - Response: 200 - Array of Task objects, 401 - Unauthorized, 403 - Forbidden
  - Authentication: Required, validates user_id matches token identity

- `POST /api/{user_id}/tasks`
  - Description: Create a new task for a user
  - Headers: Authorization: Bearer <token>
  - Request Body: { "title": "Task title", "description": "Optional description" }
  - Response: 201 - Created Task object, 401 - Unauthorized, 403 - Forbidden
  - Authentication: Required, validates user_id matches token identity

- `GET /api/{user_id}/tasks/{id}`
  - Description: Retrieve a specific task by ID
  - Headers: Authorization: Bearer <token>
  - Response: 200 - Task object, 401 - Unauthorized, 403 - Forbidden, 404 - Not Found
  - Authentication: Required, validates user_id matches token identity, validates task belongs to user

- `PUT /api/{user_id}/tasks/{id}`
  - Description: Update an existing task
  - Headers: Authorization: Bearer <token>
  - Request Body: { "title": "Updated title", "description": "Updated description" }
  - Response: 200 - Updated Task object, 401 - Unauthorized, 403 - Forbidden, 404 - Not Found
  - Authentication: Required, validates user_id matches token identity, validates task belongs to user

- `DELETE /api/{user_id}/tasks/{id}`
  - Description: Delete a task
  - Headers: Authorization: Bearer <token>
  - Response: 204 - No Content, 401 - Unauthorized, 403 - Forbidden, 404 - Not Found
  - Authentication: Required, validates user_id matches token identity, validates task belongs to user

- `PATCH /api/{user_id}/tasks/{id}/complete`
  - Description: Toggle task completion status
  - Headers: Authorization: Bearer <token>
  - Request Body: { "completed": true/false }
  - Response: 200 - Updated Task object, 401 - Unauthorized, 403 - Forbidden, 404 - Not Found
  - Authentication: Required, validates user_id matches token identity, validates task belongs to user

### quickstart.md

# Quick Start Guide: Todo Full-Stack Web Application

## Prerequisites
- Node.js 18+ installed
- Python 3.9+ installed
- Neon Serverless PostgreSQL account and database created
- Basic familiarity with Next.js and FastAPI

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Backend Setup**
   ```bash
   # Navigate to backend directory
   cd backend

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install fastapi uvicorn sqlmodel pyjwt python-multipart python-dotenv better-exceptions
   ```

3. **Frontend Setup**
   ```bash
   # Navigate to frontend directory
   cd frontend

   # Install dependencies
   npm install
   ```

4. **Environment Configuration**
   Create `.env` files in both backend and frontend with appropriate configuration:

   **Backend .env**:
   ```
   DATABASE_URL=postgresql://username:password@ep-xxxxxx.us-east-1.aws.neon.tech/dbname
   JWT_SECRET_KEY=your-super-secret-jwt-key-here-make-it-long-and-random
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

   **Frontend .env**:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   NEXTAUTH_URL=http://localhost:3000
   ```

5. **Database Initialization**
   Run database migrations to create tables:
   ```bash
   # In backend directory
   python -m scripts.init_db
   ```

6. **Run the Applications**
   ```bash
   # Terminal 1: Start backend
   cd backend
   uvicorn main:app --reload --port 8000

   # Terminal 2: Start frontend
   cd frontend
   npm run dev
   ```

7. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - Backend Documentation: http://localhost:8000/docs

## Usage
1. Visit the frontend application
2. Register a new account or sign in
3. Create, view, update, and delete tasks
4. Toggle task completion status

## Troubleshooting
- If the backend server doesn't start, check that the database URL is correctly configured
- If authentication fails, verify that the JWT secret is the same in both frontend and backend
- If the frontend can't connect to the backend, check the API URL configuration

## Development
- Backend: FastAPI with automatic documentation at `/docs`
- Frontend: Next.js with hot reloading
- Both follow the architecture and API contracts specified in the implementation plan