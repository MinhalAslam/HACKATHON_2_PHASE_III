<!--
Sync Impact Report:
- Version change: 1.1.0 → 1.2.0
- Modified principles: Enhanced Authentication & Security Rules with Phase III requirements
- Added sections: Enhanced data integrity rules, MCP tools enforcement, frontend conversation persistence
- Removed sections: None
- Templates requiring updates: ✅ All referenced templates checked for alignment
- Follow-up TODOs: None
- Rationale: MINOR version bump - added new security principles and expanded authentication requirements without breaking existing governance
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### Spec-First Development
All functionality must be explicitly defined in specifications before implementation begins. No code shall be written without a corresponding spec that clearly defines the expected behavior, inputs, outputs, and test criteria.

### Security-by-Design
Security controls must be implemented at every layer of the application. No shared state between users is permitted under any circumstances. Backend systems must never trust frontend identity without proper JWT verification. All data access must be scoped to the authenticated user.

### Agentic Development Compliance
Workflow must strictly follow the sequence: Write Spec → Generate Plan → Break into Tasks → Implement. No manual edits to generated code are allowed. All prompts must be reproducible and reviewable, and each phase must be completed and validated before moving forward.

### API-First Design
Every API behavior must be testable via HTTP requests. All API endpoints require valid JWT tokens passed via Authorization: Bearer <token> headers. Backend must verify JWT signatures using shared secrets. RESTful endpoints only, with proper HTTP methods matching intent (GET, POST, PUT, DELETE, PATCH).

### Data Integrity Assurance
Persistent storage is required - no in-memory data for production functionality. Tasks remain owned by user. Conversations belong to a single user. Messages are immutable after creation. AI responses must be persisted verbatim. Each task must be linked to a single user. Deleting a user must not expose orphaned tasks. Task completion state must be explicitly stored and toggled. Database schema must be defined before implementation.

### Production Realism
Implementation must reflect production-level realism with real databases, real authentication, and real API behaviors. Frontend and backend must maintain clear separation of concerns. Frontend must be responsive and usable on common screen sizes.

## Additional Constraints

### Architecture Requirements
- Frontend: Next.js 16+ using App Router
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (Frontend) + JWT
- Spec-Driven Tools: Claude Code + Spec-Kit Plus only

### Authentication & Security Rules
- JWT is mandatory for all chat requests
- Backend must verify JWT on every request
- Frontend identity must never be trusted
- AI agent must never receive secrets
- MCP tools must enforce user ownership
- No cross-user data access is permitted under any circumstances
- All API endpoints require a valid JWT token
- JWT must be passed via Authorization: Bearer <token> header
- Backend must verify JWT signature using shared secret
- User identity must be derived only from decoded JWT
- URL user_id must match authenticated user_id from token
- Requests without valid JWT must return 401 Unauthorized
- Task ownership must be enforced on every CRUD operation

### API Design Rules
- RESTful endpoints only
- HTTP methods must match intent (GET, POST, PUT, DELETE, PATCH)
- No endpoint may expose or modify data belonging to another user
- Error responses must use proper HTTP status codes
- API behavior must remain consistent across frontend and backend

### Frontend Rules (Chat UI)
- Chat UI must use authenticated session
- JWT must be attached automatically
- Conversation must resume after refresh
- UI must reflect backend-confirmed state only
- Errors must be shown clearly but safely
- No optimistic updates without backend confirmation
- UI must be responsive and usable on common screen sizes
- Authentication state must be respected in UI behavior
- API client must automatically attach JWT to requests
- Frontend must never hardcode user identity
- All task views must reflect backend-filtered data only

### Prohibited Actions
- No server-side sessions
- No direct DB access from frontend
- No bypassing MCP tools
- No AI hallucinated task state
- No silent failures

### Validation Requirements
Phase III is considered complete when:
- All authentication flows are JWT-based
- All API endpoints validate JWT tokens
- Frontend correctly resumes conversations after refresh
- No cross-user data leakage exists
- MCP tools enforce user ownership
- AI agent never receives or stores secrets

### Quality & Review Standards
- Specs must be clear enough for independent implementation
- No ambiguous requirements
- No undocumented behavior
- Each spec must have measurable success criteria
- Failure cases must be explicitly defined

## Development Workflow

### Development Principles
- Spec-first development (no implementation before specification)
- Deterministic, reviewable outputs at every phase
- Separation of concerns (frontend, backend, auth clearly decoupled)
- No manual edits to generated code during agentic implementation

### Quality Gates
- All functionality must be explicitly defined in specs before implementation
- Every API behavior must be testable via HTTP requests
- All changes must pass through the spec → plan → tasks → implement workflow
- Code reviews must verify compliance with all constitutional principles

## Governance

**Version**: 1.2.0
**Ratification Date**: 2026-02-08
**Last Amended**: 2026-02-08

All development activities must comply with this constitution. Any deviation requires explicit amendment to this document with proper justification and approval. Development teams must ensure that all deliverables align with the stated principles and constraints. The constitution serves as the authoritative source for development practices and takes precedence over any conflicting guidelines.

### Amendment Procedure
1. Propose changes with clear rationale and impact analysis
2. Update version according to semantic versioning:
   - MAJOR: Backward incompatible governance/principle changes
   - MINOR: New principles or materially expanded guidance
   - PATCH: Clarifications, wording fixes, non-semantic refinements
3. Update LAST_AMENDED_DATE to change date
4. Propagate changes to dependent templates and documentation
5. Document changes in Sync Impact Report comment at top of file

### Compliance Review
All feature specifications, implementation plans, and tasks must reference this constitution and demonstrate compliance with its principles. Code reviews must verify adherence to these standards.

Version: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): Date when constitution was originally adopted | **Last Amended**: 2026-02-05