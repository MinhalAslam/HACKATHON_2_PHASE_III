---
id: 11
title: Complete Auth Implementation
stage: impl
date: 2026-02-05
surface: agent
model: Claude Sonnet 4.5
feature: 1-todo-web-app
branch: 1-todo-web-app
user: AA
command: /sp.implement
labels: [implementation,authentication,security,jwt,authorization]
links:
  spec: specs/1-todo-web-app/spec-auth-security.md
  plan: specs/1-todo-web-app/plan-auth-security.md
  tasks: specs/1-todo-web-app/tasks.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/src/routers/auth.py
 - backend/src/utils/auth.py
 - backend/src/routers/tasks.py
 - backend/src/services/task_service.py
 - frontend/src/context/AuthContext.tsx
 - frontend/src/components/ProtectedRoute.tsx
 - frontend/src/app/login/page.tsx
 - frontend/src/lib/api.ts
 - frontend/src/components/LoadingSpinner.tsx
 - backend/test_auth_validation.py
 - backend/test_e2e_flows.py
 - backend/security_review_report.md
 - specs/1-todo-web-app/tasks.md
tests:
 - null
---

## Prompt

```
You are implementing **Spec 2: Authentication & API Security (JWT)**
for the Todo Full-Stack Web Application.

You MUST follow spec-driven development strictly.
Do not invent features outside the spec.
Do not modify unrelated functionality.
Do not require manual code edits after generation.

--------------------------------------------
CONTEXT
--------------------------------------------

Backend:
- Python FastAPI
- SQLModel
- Existing task CRUD endpoints already implemented

Frontend:
- Next.js 16+
- Better Auth used for authentication

Goal:
Secure the backend API using JWT-based authentication and authorization,
ensuring strict user isolation for all task operations.

--------------------------------------------
REQUIREMENTS (MANDATORY)
--------------------------------------------

Authentication:
- Better Auth must be configured to issue JWT tokens on login
- JWT must contain a unique user identifier
- JWT must expire automatically
- JWT must be sent via HTTP header:
  Authorization: Bearer <token>

Backend JWT verification:
- Extract JWT from Authorization header
- Verify JWT signature using shared secret
- Reject missing, invalid, or expired tokens
- Decode JWT to obtain authenticated user identity
- Authentication must be stateless (no server sessions)

Authorization enforcement:
- Every API endpoint must require a valid JWT
- Authenticated user identity must come ONLY from JWT
- URL `{user_id}` must match user_id from JWT
- Reject requests when user_id does not match
- Enforce task ownership on every CRUD operation
- Prevent cross-user data access under all conditions

Error handling:
- Missing token → 401 Unauthorized
- Invalid or expired token → 401 Unauthorized
- user_id mismatch → 403 Forbidden
- Use proper HTTP status codes consistently

Security constraints:
- Backend must never trust frontend identity
- Backend must never call frontend to verify users
- JWT secret must be read from environment variables
- No hardcoded secrets
- No auth bypass for any endpoint

--------------------------------------------
IMPLEMENTATION GUIDELINES
--------------------------------------------

- Implement JWT verification using FastAPI middleware or dependency
- Apply authentication globally or explicitly to all routes
- Ensure existing task endpoints remain functionally unchanged
- Modify only what is required to secure the API
- Keep logic clean, readable, and reproducible

--------------------------------------------
DELIVERABLES
--------------------------------------------

1. Backend JWT verification logic
2. Auth enforcement applied to all API routes
3. Authorization checks enforcing user isolation
4. Updated API behavior matching Spec 2 success criteria

--------------------------------------------
VALIDATION CHECKS (MUST PASS)
--------------------------------------------

- API request without JWT returns 401
- API request with invalid JWT returns 401
- API request with expired JWT returns 401
- Authenticated user cannot access another user's tasks
- URL user_id mismatch is rejected
- Valid JWT + correct us
```

## Response snapshot

Successfully implemented complete authentication and API security for the Todo Full-Stack Web Application. Delivered: 1) Backend JWT verification logic with token validation and error handling, 2) Auth enforcement applied to all API routes with proper 401/403 status codes, 3) Authorization checks enforcing user isolation and task ownership, 4) Updated API behavior matching Spec 2 success criteria. Frontend authentication components created including protected routes, login/signup flows, and state management. Backend includes proper validation, middleware, and security measures. Comprehensive tests and security review included.

## Outcome

- ✅ Impact: Complete JWT-based security implementation with user isolation
- 🧪 Tests: End-to-end and validation tests created for all security features
- 📁 Files: Multiple backend and frontend files updated with security features
- 🔁 Next prompts: Ready for deployment and further feature development
- 🧠 Reflection: Implementation follows all spec requirements with proper separation of concerns

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Deploy and test the secured application