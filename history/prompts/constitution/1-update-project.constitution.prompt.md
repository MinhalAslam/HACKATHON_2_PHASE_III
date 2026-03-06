---
id: 1
title: Update Project Constitution
stage: constitution
date: 2026-02-05
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: AA
command: /sp.constitution
labels: [constitution,spec-driven-development,security]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - null
---

## Prompt

```
/sp.constitution

Project: Todo Full-Stack Web Application (Hackathon Phase 2)

Objective:
Transform an in-memory console Todo application into a secure, multi-user,
full-stack web application using spec-driven development and agentic coding.
All implementation must be generated via Claude Code using Spec-Kit Plus,
with no manual coding.

Development Principles:
- Spec-first development (no implementation before specification)
- Deterministic, reviewable outputs at every phase
- Security-by-design (user isolation enforced at every layer)
- Separation of concerns (frontend, backend, auth clearly decoupled)
- Production realism (real DB, real auth, real API behavior)

Core Standards:
- All functionality must be explicitly defined in specs before implementation
- Every API behavior must be testable via HTTP requests
- No shared state between users under any circumstance
- Backend must never trust frontend identity without JWT verification
- All data access must be scoped to the authenticated user

Architecture Constraints:
- Frontend: Next.js 16+ using App Router
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (Frontend) + JWT
- Spec-Driven Tools: Claude Code + Spec-Kit Plus only

Authentication & Security Rules:
- All API endpoints require a valid JWT token
- JWT must be passed via Authorization: Bearer <token> header
- Backend must verify JWT signature using shared secret
- User identity must be derived only from decoded JWT
- URL user_id must match authenticated user_id from token
- Requests without valid JWT must return 401 Unauthorized
- Task ownership must be enforced on every CRUD operation

API Design Rules:
- RESTful endpoints only
- HTTP methods must match intent (GET, POST, PUT, DELETE, PATCH)
- No endpoint may expose or modify data belonging to another user
- Error responses must use proper HTTP status codes
- API behavior must remain consistent across frontend and backend

Data Integrity Rules:
- Persistent storage required (no in-memory data)
- Each task must be linked to a single user
- Deleting a user must not expose orphaned tasks
- Task completion state must be explicitly stored and toggled
- Database schema must be defined before implementation

Frontend Rules:
- UI must be responsive and usable on common screen sizes
- Authentication state must be respected in UI behavior
- API client must automatically attach JWT to requests
- Frontend must never hardcode user identity
- All task views must reflect backend-filtered data only

Agentic Development Constraints:
- Workflow must strictly follow:
  Write Spec → Generate Plan → Break into Tasks → Implement
- No manual edits to generated code
- Prompts must be reproducible and reviewable
- Each phase must be completed and validated before moving forward

Quality & Review Standards:
- Specs must be clear enough for independent implementation
- No ambiguous requirements
- No undocumented behavior
- Each spec must have measurable success criteria
- Failure cases must be explicitly defined

```

## Response snapshot

Updated the project constitution file with specific principles and constraints for the Todo Full-Stack Web Application project. Created six core principles: Spec-First Development, Security-by-Design, Agentic Development Compliance, API-First Design, Data Integrity Assurance, and Production Realism. Added sections for Additional Constraints, Development Workflow, and Governance, incorporating all the architectural requirements, authentication rules, and quality standards specified in the user input.

## Outcome

- ✅ Impact: Project constitution file updated with comprehensive principles and constraints
- 🧪 Tests: N/A for documentation update
- 📁 Files: .specify/memory/constitution.md updated
- 🔁 Next prompts: Proceed with spec generation based on new constitution
- 🧠 Reflection: Constitution now properly captures all project requirements and constraints

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Generate feature spec based on updated constitution