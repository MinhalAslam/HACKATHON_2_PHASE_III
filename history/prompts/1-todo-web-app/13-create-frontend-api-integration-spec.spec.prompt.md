---
id: 13
title: Create Frontend API Integration Spec (Spec 3)
stage: spec
date: 2026-02-07
surface: agent
model: claude-opus-4-5-20251101
feature: 1-todo-web-app
branch: master
user: AA
command: /sp.specify
labels: ["frontend", "api-integration", "authentication", "specification", "next.js", "better-auth"]
links:
  spec: specs/1-todo-web-app/spec-3-frontend-api-integration.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/1-todo-web-app/spec-3-frontend-api-integration.md
tests:
 - Manual testing checklist provided in specification
 - User story acceptance scenarios defined
---

## Prompt

/sp.specify /sp.specify – Spec 3: Frontend Web Application & API Integration

Project: Todo Full-Stack Web Application (Spec 3)

Target:
Build a production-ready, authenticated frontend using Next.js App Router
that securely integrates with an existing FastAPI backend via JWT.

Audience:
- Evaluators reviewing spec-driven development
- Developers validating frontend–backend integration correctness

Scope:
Frontend-only implementation. Backend is treated as a fixed, trusted API.

--------------------------------------------------
CORE OBJECTIVES
--------------------------------------------------

Authentication:
- Implement user signup and signin using Better Auth
- Manage authentication state via JWT
- Automatically attach JWT to all API requests
- Never infer, hardcode, or spoof user identity on frontend

API Integration:
- Communicate only with existing backend endpoints
- Respect backend authorization and user isolation
- Handle unauthorized access safely and predictably

Task Management UI:
- List tasks for authenticated user only
- Create new tasks (title, description)
- Update existing tasks
- Delete tasks
- Toggle task completion
- Reflect backend state immediately after API responses

--------------------------------------------------
REQUIRED API ENDPOINTS
--------------------------------------------------

GET    /api/{user_id}/tasks
POST   /api/{user_id}/tasks
GET    /api/{user_id}/tasks/{id}
PUT    /api/{user_id}/tasks/{id}
DELETE /api/{user_id}/tasks/{id}
PATCH  /api/{user_id}/tasks/{id}/complete

All requests:
- Must include Authorization: Bearer <JWT>
- Must rely on backend for user ownership enforcement

--------------------------------------------------
ROUTING & ACCESS CONTROL
--------------------------------------------------

- Public routes:
  - /signup
  - /login

- Protected routes:
  - /tasks
  - /tasks/[id]

Rules:
- Unauthenticated users are redirected to /login
- Authenticated users cannot access auth pages unnecessarily
- Session persists across reloads using Better Auth

--------------------------------------------------
UI / UX REQUIREMENTS
--------------------------------------------------

- Responsive layout (desktop, tablet)
- Clear completed vs incomplete task indicators
- Loading states for async operations
- Error states for failed API calls
- No animations or advanced design systems

--------------------------------------------------
CONSTRAINTS
--------------------------------------------------

- Frontend only (no backend logic)
- No feature additions beyond this spec
- No manual post-generation fixes
- Deterministic, reproducible behavior
- Use Next.js 16+ App Router conventions

--------------------------------------------------
SUCCESS CRITERIA
--------------------------------------------------

- Auth flow works end-to-end using Better Auth
- JWT is attached to every backend request
- Unauthorized access is blocked and redirected
- Tasks shown belong only to authenticated user
- CRUD + toggle operations function correctly
- UI always reflects backend state
- 401 responses handled gracefully

## Response snapshot

Created comprehensive specification document: `spec-3-frontend-api-integration.md`

**Specification Structure:**
1. Executive Summary - Established frontend-only scope with backend as fixed API
2. User Scenarios & Testing - 7 prioritized user stories (P1-P2) with independent test criteria:
   - User Story 1: User Authentication Flow (P1)
   - User Story 2: Authenticated Task List Viewing (P1)
   - User Story 3: Task Creation (P1)
   - User Story 4: Task Editing and Updates (P2)
   - User Story 5: Task Deletion (P2)
   - User Story 6: Task Completion Toggle (P2)
   - User Story 7: Protected Route Access Control (P1)
3. Edge Cases - Defined 7 critical edge case scenarios (JWT expiration, network timeouts, race conditions, etc.)
4. Requirements - 34 functional requirements organized by:
   - Authentication & Session Management (FR-001 to FR-007)
   - Routing & Access Control (FR-008 to FR-012)
   - API Integration (FR-013 to FR-019)
   - Task Management UI (FR-020 to FR-030)
   - UI/UX Requirements (FR-031 to FR-034)
5. Success Criteria - 14 measurable outcomes (SC-001 to SC-014)
6. Technical Architecture - Detailed architecture including:
   - Technology stack (Next.js 16+, Better Auth, Tailwind CSS)
   - Project structure with file organization
   - API client implementation with JWT interceptor
   - Authentication flow diagrams
   - Route protection middleware example
7. Constraints - Clear boundaries (frontend-only, no backend logic, Next.js 16+ conventions)
8. Non-Functional Requirements - Security, performance, reliability, usability (NFR-001 to NFR-014)
9. Testing Strategy - Comprehensive manual testing checklist with 6 test categories
10. Implementation Plan Reference - Links to plan and tasks documents
11. Acceptance Criteria Summary - 10-point checklist
12. Risks and Mitigation - 5 identified risks with mitigation strategies
13. Definition of Done - 13-point checklist

**Key Design Decisions:**
- Frontend MUST never infer, hardcode, or spoof user identity
- All user context and authorization come from backend via JWT
- Better Auth manages authentication state and JWT tokens
- API client automatically attaches JWT to all requests
- Middleware enforces route protection at Next.js level
- UI updates immediately after successful API responses
- All API errors handled gracefully with user-friendly messages

**Security Principles:**
- JWT tokens stored securely (httpOnly cookies preferred)
- Authorization header automatically attached to all API requests
- 401 responses trigger logout and redirect to /login
- No client-side authorization logic - all decisions from backend
- User isolation enforced entirely by backend API

**File Created:**
- specs/1-todo-web-app/spec-3-frontend-api-integration.md (comprehensive 400+ line specification)

## Outcome

- ✅ Impact: Created comprehensive frontend specification covering all authentication, API integration, and UI requirements for Next.js App Router implementation with Better Auth
- 🧪 Tests: Manual testing checklist with 6 test categories (authentication, route protection, task operations, API integration, user isolation, edge cases); acceptance scenarios for 7 user stories
- 📁 Files: specs/1-todo-web-app/spec-3-frontend-api-integration.md (new)
- 🔁 Next prompts: /sp.plan to create architectural plan for frontend implementation; /sp.tasks to generate granular implementation tasks; /sp.adr if significant architectural decisions require documentation
- 🧠 Reflection: Specification successfully balances comprehensive requirements with clear constraints. Strong emphasis on security principles (no client-side user inference, backend-only authorization). User stories are independently testable and prioritized. Technical architecture provides concrete implementation guidance (API client structure, middleware examples). Edge cases and risk mitigation proactively address failure scenarios.

## Evaluation notes (flywheel)

- Failure modes observed: None during specification creation. Potential implementation risks identified and documented (Better Auth configuration complexity, JWT token management, API integration failures, user isolation vulnerabilities, session persistence issues).
- Graders run and results (PASS/FAIL): N/A - Specification phase (no code implementation yet)
- Prompt variant (if applicable): Standard /sp.specify command with detailed user requirements
- Next experiment (smallest change to try): Proceed to /sp.plan to design implementation architecture, then /sp.tasks to create granular testable tasks. Consider whether Better Auth JWT configuration requires an ADR.
