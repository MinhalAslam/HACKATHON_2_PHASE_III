---
id: 3
title: Update Todo Web App Spec
stage: spec
date: 2026-02-05
surface: agent
model: Claude Sonnet 4.5
feature: 1-todo-web-app
branch: 1-todo-web-app
user: AA
command: /sp.specify
labels: [spec,full-stack,todo-application,authentication,security]
links:
  spec: specs/1-todo-web-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/1-todo-web-app/spec.md
 - specs/1-todo-web-app/checklists/requirements.md
tests:
 - null
---

## Prompt

```
/sp.specify Todo Full-Stack Web Application (Hackathon Phase 2)

Target audience:
Hackathon evaluators and developers assessing spec-driven,
agentic full-stack web application development.

Primary goal:
Convert a single-user, in-memory console Todo application into a
secure, multi-user, full-stack web application with persistent storage,
RESTful APIs, and JWT-based authentication.

Core objectives:
- Enable multiple authenticated users to manage their own tasks
- Ensure strict user isolation at API and database levels
- Demonstrate spec-driven, agentic development using Claude Code
- Build a realistic production-style architecture

Functional success criteria:
- Users can sign up and sign in via Better Auth
- All authenticated users receive a JWT token
- JWT token is required for every API request
- Users can create tasks with title and description
- Users can list only their own tasks
- Users can retrieve task details by ID
- Users can update existing tasks
- Users can delete tasks
- Users can toggle task completion state
- Task data persists across sessions and reloads

Authentication & authorization requirements:
- Better Auth must be configured to issue JWT tokens
- JWT must be included in Authorization: Bearer <token> header
- Backend must verify JWT signature using shared secret
- User identity must be derived solely from decoded JWT
- Backend must reject requests with:
  - Missing token
  - Invalid token
  - Expired token
- URL user_id must match authenticated user_id from token
- All task operations must enforce ownership checks

API requirements:
- RESTful API design using FastAPI
- Supported HTTP methods:
  - GET, POST, PUT, DELETE, PATCH
- Required endpoints:
  - GET    /api/{user_id}/tasks
  - POST   /api/{user_id}/tasks
  - GET    /api/{user_id}/tasks/{id}
  - PUT    /api/{user_id}/tasks/{id}
  - DELETE /api/{user_id}/tasks/{id}
  - PATCH  /api/{user_id}/tasks/{id}/complete
- All endpoints require valid JWT authentication
- Proper HTTP status codes must be returned for all outcomes

Data and persistence requirements:
- Persistent storage using Neon Serverless PostgreSQL
- SQLModel used for ORM and schema definition
- Each task must be associated with exactly one user
- Database queries must always be filtered by authenticated user
- Task completion state must be stored explicitly
- No in-memory task storage permitted

Frontend requirements:
- Built using Next.js 16+ with App Router
- Authentication handled via Better Auth
- JWT token must be attached to every API request
- UI must reflect authentication state
- Users must not be able to access task UI without logging in
- Task views must reflect backend-filtered results only
- Frontend must not trust or infer user identity locally

Technical constraints:
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Frontend: Next.js 16+
- Authentication: Better Auth + JWT
- Shared JWT secret via environment variables
- Spec-driven tooling: Claude Code + Spec-Kit Plus
- No manual coding or post-generation edits

Quality and correctne
```

## Response snapshot

Updated the Todo Full-Stack Web Application specification with more detailed requirements from the user's enhanced prompt. The updated spec includes improved user stories with focus on authentication and security, comprehensive functional requirements covering Better Auth integration, JWT authentication, and user isolation, and detailed success criteria measuring authentication performance, security enforcement, and task management capabilities.

## Outcome

- ✅ Impact: Specification enhanced with detailed security and API requirements
- 🧪 Tests: N/A for specification update
- 📁 Files: specs/1-todo-web-app/spec.md and checklists/requirements.md updated
- 🔁 Next prompts: Proceed with /sp.plan to generate implementation plan
- 🧠 Reflection: Enhanced spec now covers all detailed requirements including Better Auth, JWT security, and specific API endpoints

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Generate implementation plan based on enhanced specification