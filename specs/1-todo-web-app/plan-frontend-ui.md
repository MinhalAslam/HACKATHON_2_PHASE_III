# Implementation Plan: Frontend Web Application & API Integration

**Feature**: Frontend Web Application & API Integration
**Created**: 2026-02-05
**Status**: Draft
**Branch**: 1-todo-web-app

## Technical Context

This implementation will create a responsive, authenticated frontend web application that consumes secured backend APIs and provides full Todo management functionality to authenticated users only. The frontend will be built with Next.js 16+ using App Router, integrate Better Auth for authentication, and consume the secured REST API endpoints with automatic JWT token management.

**Technologies Stack**:
- Frontend Framework: Next.js 16+ with App Router
- Styling: Tailwind CSS for responsive design
- HTTP Client: Axios for API requests
- Authentication: Better Auth for user management
- State Management: React Context or built-in React hooks
- Form Handling: React Hook Form (optional but recommended)

**Dependencies**:
- next: ^16.0.0
- react: ^19.0.0
- react-dom: ^19.0.0
- axios: ^1.6.0
- better-auth: ^0.0.0-beta.0
- tailwindcss: ^3.3.0
- react-hook-form: ^7.47.0 (optional)
- @types/node: ^20
- @types/react: ^19
- @types/react-dom: ^19

## Architecture Overview

The frontend architecture will follow a component-based approach with clear separation between authentication, UI, and API logic:

1. **Authentication Layer** (Better Auth):
   - Handles user signup/login/logout flows
   - Manages JWT token storage and lifecycle
   - Provides authentication state to the application

2. **API Layer** (Axios Client):
   - Centralized API request handling
   - Automatic JWT token attachment
   - Error handling and response processing
   - Request/response interceptors for consistent behavior

3. **UI Layer** (Next.js Components):
   - Responsive layout and page components
   - Task management forms and views
   - Loading and error state components
   - Protected route wrappers

4. **Routing Layer** (Next.js App Router):
   - Public routes (login, signup)
   - Protected routes (dashboard, tasks)
   - Route protection logic

## Constitution Check

This plan aligns with all constitutional principles:

✅ **Spec-First Development**: Implementation follows the detailed frontend specification
✅ **Security-by-Design**: JWT-based authentication with user isolation enforced at every layer
✅ **Agentic Development Compliance**: Following spec → plan → tasks → implement workflow
✅ **API-First Design**: API consumption via REST endpoints with proper authentication
✅ **Data Integrity Assurance**: Frontend only displays backend-filtered results
✅ **Production Realism**: Real authentication system with proper security measures

## Phase 0: Research & Resolution of Unknowns

### research.md

#### Decision: Strategy for Protecting Authenticated Routes
- **Chosen**: Higher-order component wrapper that checks authentication state before rendering
- **Rationale**: Provides consistent protection across the application; easy to apply to any route; fits well with Next.js App Router patterns
- **Alternatives considered**:
  - Middleware approach: More complex for client-side authentication state
  - Individual route checks: Repetitive and error-prone

#### Decision: Method for Attaching JWT to API Requests
- **Chosen**: Axios interceptors to automatically attach tokens to all requests
- **Rationale**: Centralized approach that ensures all API calls have proper authentication; reduces repetitive code; handles token management consistently
- **Alternatives considered**:
  - Manual attachment per request: Error-prone and repetitive
  - Custom hook per component: Inconsistent application

#### Decision: Global vs Per-Request API Client Design
- **Chosen**: Singleton API client with global configuration
- **Rationale**: Provides consistent behavior across the application; easier to manage interceptors and error handling; better for performance
- **Alternatives considered**:
  - Per-component instances: Inconsistent configuration and management
  - Multiple client instances: Resource waste

#### Decision: UI Behavior on Authentication Failure (401 Handling)
- **Chosen**: Axios response interceptor that redirects to login on 401
- **Rationale**: Centralized error handling; consistent user experience; automatic cleanup of authentication state
- **Alternatives considered**:
  - Component-level handling: Inconsistent behavior across the app
  - Manual check on each request: Repetitive code

#### Decision: State Management Approach for Task Data
- **Chosen**: Combination of React hooks (useState, useReducer) and React Query for server state
- **Rationale**: Leverages familiar React patterns; React Query provides excellent server state management; scalable for complex UI states
- **Alternatives considered**:
  - Full Redux implementation: Overkill for this application size
  - Pure component state: Difficult to share across components

#### Decision: Error and Loading State Handling Conventions
- **Chosen**: Reusable loading and error components with consistent styling
- **Rationale**: Provides consistent UX across the application; reduces code duplication; easier to maintain
- **Alternatives considered**:
  - Inline loading/error states: Inconsistent and repetitive
  - Different patterns per component: Poor maintainability

## Phase 1: Design & Contracts

### data-model.md

#### Authentication State Entity
- **Structure**:
  - isAuthenticated: Boolean (whether user is currently authenticated)
  - user: Object (user profile information)
  - token: String (JWT token)
  - isLoading: Boolean (whether authentication state is being determined)
  - error: String (any authentication-related errors)
- **Operations**:
  - login(credentials): Initiate login process
  - logout(): Clear authentication state
  - refresh(): Verify and refresh authentication state

#### Task Data Entity (Frontend Representation)
- **Structure**:
  - id: String (unique identifier)
  - title: String (task title, max 200 characters)
  - description: String (optional task description)
  - completed: Boolean (completion status)
  - createdAt: String (ISO date string)
  - updatedAt: String (ISO date string)
- **Operations**:
  - create(taskData): Create a new task
  - update(taskId, updates): Update existing task
  - delete(taskId): Delete a task
  - toggleCompletion(taskId): Toggle completion status

#### API Response Entity
- **Structure**:
  - data: Mixed (response data payload)
  - status: Number (HTTP status code)
  - statusText: String (HTTP status text)
  - headers: Object (response headers)
- **Validation**:
  - All API responses must conform to expected structure
  - Error responses must include appropriate error messages

### API Contracts

#### Frontend-to-Backend API Calls
- `POST /api/auth/login`
  - Description: Authenticate user and obtain JWT
  - Request Body: { email: String, password: String }
  - Response: 200 - { access_token: String, token_type: String }, 401 - { detail: String }
  - Authorization: None required

- `POST /api/auth/register`
  - Description: Register new user
  - Request Body: { email: String, password: String }
  - Response: 200 - User object, 400 - { detail: String }
  - Authorization: None required

- `GET /api/{user_id}/tasks`
  - Description: Retrieve user's tasks
  - Headers: Authorization: Bearer <token>
  - Response: 200 - Array of Task objects, 401 - Unauthorized, 403 - Forbidden
  - Authorization: JWT required

- `POST /api/{user_id}/tasks`
  - Description: Create new task
  - Headers: Authorization: Bearer <token>
  - Request Body: { title: String, description: String }
  - Response: 201 - Created Task object, 401 - Unauthorized, 403 - Forbidden
  - Authorization: JWT required

- `PUT /api/{user_id}/tasks/{id}`
  - Description: Update task
  - Headers: Authorization: Bearer <token>
  - Request Body: { title: String, description: String }
  - Response: 200 - Updated Task object, 401 - Unauthorized, 403 - Forbidden, 404 - Not Found
  - Authorization: JWT required

- `DELETE /api/{user_id}/tasks/{id}`
  - Description: Delete task
  - Headers: Authorization: Bearer <token>
  - Response: 204 - No Content, 401 - Unauthorized, 403 - Forbidden, 404 - Not Found
  - Authorization: JWT required

- `PATCH /api/{user_id}/tasks/{id}/complete`
  - Description: Toggle task completion
  - Headers: Authorization: Bearer <token>
  - Request Body: { completed: Boolean }
  - Response: 200 - Updated Task object, 401 - Unauthorized, 403 - Forbidden, 404 - Not Found
  - Authorization: JWT required

### quickstart.md

# Quick Start Guide: Frontend Web Application & API Integration

## Prerequisites
- Node.js 18+ installed
- Backend API running and accessible
- NEXT_PUBLIC_API_URL configured to point to backend
- NEXT_PUBLIC_JWT_SECRET matches backend configuration

## Setup Instructions

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Environment Configuration**
   Create `.env.local` file with:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   NEXT_PUBLIC_JWT_SECRET=your-shared-jwt-secret
   ```

4. **Run Development Server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Access the Application**
   - Open http://localhost:3000 in your browser
   - Application will automatically reload on code changes

## Development Structure

- **Pages**: Located in `src/app/` following App Router conventions
- **Components**: Reusable UI elements in `src/components/`
- **Libraries**: API client and utilities in `src/lib/`
- **Types**: TypeScript definitions in `src/types/`
- **Context**: Global state management in `src/context/`

## Running Tests
```bash
npm run test
# or for watch mode
npm run test:watch
```

## Building for Production
```bash
npm run build
npm start
```

## Key Architecture Points
- Authentication state is managed globally via React Context
- API calls automatically include JWT tokens via Axios interceptors
- Protected routes redirect unauthenticated users to login
- Form submissions handle loading and error states appropriately
- Responsive design works across mobile, tablet, and desktop