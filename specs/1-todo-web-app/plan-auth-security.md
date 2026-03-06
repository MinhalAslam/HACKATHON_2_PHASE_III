# Implementation Plan: Authentication & API Security (JWT)

**Feature**: Authentication & API Security (JWT)
**Created**: 2026-02-05
**Status**: Draft
**Branch**: 1-todo-web-app

## Technical Context

This implementation will secure the Todo application by implementing JWT-based authentication and authorization, ensuring strict user isolation across all backend API operations. The plan includes configuring Better Auth for JWT issuance, implementing JWT verification in FastAPI, and enforcing authorization checks on all API endpoints.

**Technologies Stack**:
- Backend: Python FastAPI with JWT token verification
- Frontend: Next.js 16+ with Better Auth integration
- ORM: SQLModel for any additional security-related models
- Database: Neon Serverless PostgreSQL for user management
- Authentication: Better Auth for initial authentication, JWT for subsequent API requests

**Dependencies**:
- PyJWT for JWT handling
- python-jose[cryptography] for JWT encoding/decoding
- Better Auth for frontend authentication
- FastAPI dependencies for security checks

## Architecture Overview

The security architecture will follow a layered approach with clear separation between authentication and authorization:

1. **Frontend Authentication Layer** (Better Auth):
   - Handles initial user login/registration
   - Receives JWT tokens from authentication server
   - Manages JWT token storage and lifecycle

2. **API Security Layer** (FastAPI + JWT):
   - Validates JWT tokens on all protected endpoints
   - Extracts user identity from token claims
   - Matches JWT user_id with URL user_id parameter
   - Enforces task ownership on all operations

3. **Authorization Layer** (FastAPI + Database):
   - Verifies user ownership of requested resources
   - Blocks cross-user data access
   - Returns appropriate error codes for authorization failures

## Constitution Check

This plan aligns with all constitutional principles:

✅ **Spec-First Development**: Implementation follows the detailed authentication specification
✅ **Security-by-Design**: JWT-based authentication with user isolation enforced at every layer
✅ **Agentic Development Compliance**: Following spec → plan → tasks → implement workflow
✅ **API-First Design**: JWT authentication via Authorization header with proper HTTP status codes
✅ **Data Integrity Assurance**: User isolation enforced via JWT and database-level validation
✅ **Production Realism**: Real authentication system with proper security measures

## Phase 0: Research & Resolution of Unknowns

### research.md

#### Decision: JWT Verification Method in FastAPI
- **Chosen**: Using FastAPI dependencies with HTTPBearer for token extraction
- **Rationale**: Provides reusable authentication logic that can be applied to specific endpoints; allows for flexible error handling and validation; integrates well with FastAPI's dependency injection system
- **Alternatives considered**:
  - Middleware approach: More complex for selective endpoint protection
  - Decorator approach: Less flexible and harder to maintain

#### Decision: JWT Claim for Canonical User Identifier
- **Chosen**: Using 'sub' (subject) claim for user ID
- **Rationale**: Follows JWT standards; 'sub' is the standard claim for identifying the principal; includes expiration for security
- **Alternatives considered**:
  - 'user_id' custom claim: Deviates from standards
  - 'email' claim: May change over time

#### Decision: Strategy for Matching JWT user_id with URL user_id
- **Chosen**: Compare authenticated user ID from JWT with user_id path parameter in FastAPI dependencies
- **Rationale**: Provides centralized validation that can be applied consistently across endpoints; allows for clear error responses
- **Alternatives considered**:
  - Manual validation in each endpoint: Repetitive and error-prone
  - Database lookup validation: Unnecessary overhead

#### Decision: Error Response Behavior for Auth Failures
- **Chosen**: Standard HTTP 401 for authentication failures, 403 for authorization failures
- **Rationale**: Follows REST API best practices; provides clear communication about request outcomes; compatible with frontend error handling
- **Alternatives considered**:
  - Custom error codes: Non-standard and harder to integrate
  - Generic error responses: Insufficient information for clients

#### Decision: Scope of JWT Enforcement
- **Chosen**: Per-route enforcement using FastAPI dependencies
- **Rationale**: Provides fine-grained control over which routes require authentication; allows for public endpoints where appropriate; fits well with the existing architecture
- **Alternatives considered**:
  - Global middleware: Less flexible for mixed public/protected APIs
  - Per-controller enforcement: Less granular than per-route

## Phase 1: Design & Contracts

### data-model.md

#### JWT Token Entity (Conceptual, not persisted)
- **Structure**:
  - Header: Algorithm and token type
  - Payload: Claims including 'sub' (user ID), 'exp' (expiration), 'iat' (issued at)
  - Signature: Signed with shared secret
- **Validation Rules**:
  - Token must not be expired
  - Signature must be valid
  - 'sub' claim must be present and valid

#### User Identity Claims
- **Fields**:
  - sub: UUID (user identifier from database)
  - exp: Integer (expiration timestamp)
  - iat: Integer (issued at timestamp)
- **Validation**:
  - sub must correspond to a valid user in the database
  - exp must be in the future

### API Contracts

#### Authenticated Endpoints (All existing task endpoints)
- `GET /api/{user_id}/tasks`
  - Headers: Authorization: Bearer <token>
  - Validation: JWT valid, user_id matches token sub claim
  - Response: 200 - Tasks list, 401 - Unauthorized, 403 - Forbidden

- `POST /api/{user_id}/tasks`
  - Headers: Authorization: Bearer <token>
  - Validation: JWT valid, user_id matches token sub claim
  - Response: 201 - Task created, 401 - Unauthorized, 403 - Forbidden

- `GET /api/{user_id}/tasks/{id}`
  - Headers: Authorization: Bearer <token>
  - Validation: JWT valid, user_id matches token sub claim, task belongs to user
  - Response: 200 - Task details, 401 - Unauthorized, 403 - Forbidden, 404 - Not Found

- `PUT /api/{user_id}/tasks/{id}`
  - Headers: Authorization: Bearer <token>
  - Validation: JWT valid, user_id matches token sub claim, task belongs to user
  - Response: 200 - Task updated, 401 - Unauthorized, 403 - Forbidden, 404 - Not Found

- `DELETE /api/{user_id}/tasks/{id}`
  - Headers: Authorization: Bearer <token>
  - Validation: JWT valid, user_id matches token sub claim, task belongs to user
  - Response: 204 - Task deleted, 401 - Unauthorized, 403 - Forbidden, 404 - Not Found

- `PATCH /api/{user_id}/tasks/{id}/complete`
  - Headers: Authorization: Bearer <token>
  - Validation: JWT valid, user_id matches token sub claim, task belongs to user
  - Response: 200 - Task updated, 401 - Unauthorized, 403 - Forbidden, 404 - Not Found

### quickstart.md

# Quick Start Guide: Authentication & API Security Implementation

## Prerequisites
- Backend and frontend applications already set up
- Better Auth configured on frontend
- Environment variables configured with JWT secret

## Implementation Steps

1. **Configure JWT Secret**
   - Ensure JWT_SECRET_KEY is set in backend environment
   - Share the same secret with frontend for consistency

2. **Implement JWT Validation Functions**
   - Create JWT verification utilities
   - Implement token parsing and validation

3. **Create FastAPI Dependencies**
   - Create authentication dependencies
   - Create authorization validation dependencies

4. **Apply Security to Endpoints**
   - Add JWT dependencies to all protected endpoints
   - Ensure user_id matching validation

5. **Frontend Integration**
   - Verify JWT attachment to API requests
   - Implement token refresh mechanisms if needed

6. **Testing**
   - Verify authentication failures return 401
   - Verify authorization failures return 403
   - Confirm legitimate requests succeed
   - Test user isolation enforcement

## Configuration
- Set JWT_ACCESS_TOKEN_EXPIRE_MINUTES to appropriate value (recommended: 30-60 minutes)
- Ensure shared JWT_SECRET_KEY between frontend and backend
- Consider implementing token refresh mechanism for better UX