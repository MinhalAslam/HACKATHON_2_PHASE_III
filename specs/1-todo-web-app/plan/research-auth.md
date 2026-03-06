# Research Summary: Authentication & API Security (JWT)

## Decision Log

### 1. JWT Verification Method in FastAPI

**Decision**: Using FastAPI dependencies (HTTPBearer) with JWT decoding

**Rationale**:
- Provides reusable authentication logic that can be applied to specific endpoints
- Allows for flexible error handling and validation
- Integrates well with FastAPI's dependency injection system
- Enables centralized authentication logic while maintaining endpoint flexibility

**Alternatives considered**:
- Middleware approach: While effective for global authentication, this would be overly complex for selective endpoint protection where some endpoints need to be public while others require authentication
- Decorator approach: Creates tight coupling and is harder to maintain compared to the clean dependency injection system that FastAPI offers

**Implementation approach**:
- Use `HTTPBearer` scheme for token extraction
- Create a dependency function that validates JWT and extracts user information
- Apply the dependency to protected endpoints

### 2. JWT Claim for Canonical User Identifier

**Decision**: Using 'sub' (subject) claim for user ID

**Rationale**:
- Follows JWT standards and best practices (RFC 7519)
- 'sub' is the standard claim for identifying the principal (user)
- Includes 'exp' for automatic expiration handling for security
- Minimal, standardized set of claims for lightweight tokens

**Alternatives considered**:
- Custom claims (e.g., 'user_id'): While providing clarity, this deviates from standards
- Multiple claims for identity (e.g., username, email): Adds unnecessary bulk to tokens

**Claims to include**:
- `sub`: Unique user identifier (UUID)
- `exp`: Token expiration timestamp
- `iat`: Token issued timestamp

### 3. Strategy for Matching JWT user_id with URL user_id

**Decision**: Compare authenticated user ID from JWT with user_id path parameter in FastAPI dependencies

**Rationale**:
- Provides centralized validation that can be applied consistently across endpoints
- Allows for clear error responses with appropriate HTTP status codes
- Prevents users from accessing resources they don't own
- Maintains clean separation of concerns

**Alternatives considered**:
- Manual validation in each endpoint: Repetitive, error-prone, and difficult to maintain
- Database lookup validation: Adds unnecessary overhead when user identity is available in JWT

**Implementation approach**:
- Create a dependency that extracts user ID from JWT
- Compare with path parameter user_id
- Return 403 Forbidden if they don't match

### 4. Error Response Behavior for Auth Failures

**Decision**: Standard HTTP 401 for authentication failures, 403 for authorization failures

**Rationale**:
- Follows REST API best practices and HTTP specifications
- Provides clear distinction between authentication (401) and authorization (403) failures
- Compatible with frontend error handling and standard HTTP client behavior
- Industry standard approach understood by API consumers

**Status codes mapping**:
- 401 Unauthorized: Missing, invalid, or expired JWT
- 403 Forbidden: Valid JWT but insufficient privileges for requested resource
- 200/201/204: Successful requests with proper authentication
- 400: Malformed requests

**Alternatives considered**:
- Custom error codes: Non-standard and harder to integrate with existing tools
- Generic 400 responses: Insufficient specificity for different error types

### 5. Scope of JWT Enforcement

**Decision**: Per-route enforcement using FastAPI dependencies

**Rationale**:
- Provides fine-grained control over which routes require authentication
- Allows for mixed public/protected API architectures
- Fits well with FastAPI's design philosophy and dependency injection system
- Enables clear separation between public and protected endpoints

**Alternatives considered**:
- Global middleware: Too restrictive for APIs that need to serve both public and protected content
- Per-controller enforcement: Less granular control than per-route level

**Implementation approach**:
- Create reusable dependency functions for different security levels
- Apply dependencies selectively to routes based on security requirements
- Maintain flexibility for future public endpoints

### 6. Token Storage and Lifecycle Management

**Decision**: Store JWT in browser storage (localStorage or sessionStorage) with proper security considerations

**Rationale**:
- Provides seamless user experience with automatic token inclusion
- Works well with single-page applications
- Enables token persistence across browser sessions (with localStorage)

**Security considerations**:
- Protect against XSS by sanitizing all user inputs
- Consider using HttpOnly cookies for higher security requirements
- Implement token refresh mechanisms for long-lived sessions

**Alternatives considered**:
- HttpOnly cookies: Better security but more complex implementation
- Memory storage: More secure but requires re-authentication on page refresh

### 7. Token Refresh Strategy

**Decision**: Implement silent refresh using refresh tokens for better UX

**Rationale**:
- Improves user experience by preventing unexpected logouts
- Maintains security by using short-lived access tokens
- Allows for smooth transition when tokens expire

**Implementation approach**:
- Issue both access and refresh tokens
- Use refresh tokens to silently acquire new access tokens
- Handle refresh token expiration gracefully

**Alternatives considered**:
- No refresh mechanism: Poor UX with frequent re-authentication
- Long-lived tokens: Increased security risk if compromised

### 8. Backend User Lookup Strategy

**Decision**: Validate user exists in database after JWT verification

**Rationale**:
- Prevents access for disabled or deleted accounts
- Provides additional layer of security
- Enables enforcement of user-specific policies

**Implementation approach**:
- Verify JWT signature and expiration first
- Query database to confirm user exists and is active
- Return user object with necessary permissions

**Alternatives considered**:
- JWT-only validation: Faster but doesn't account for account status changes
- Database-first validation: More secure but adds overhead to every request

### 9. Authorization Check Implementation

**Decision**: Perform authorization checks at the service layer

**Rationale**:
- Centralizes business logic for access control
- Enables reuse across different entry points (API, CLI, etc.)
- Maintains separation of concerns between authentication and authorization

**Implementation approach**:
- Authenticate user identity at API layer
- Validate resource ownership at service layer
- Return appropriate errors when authorization fails

**Alternatives considered**:
- API-layer authorization: Tight coupling between routing and business logic
- Database-level enforcement: Limited flexibility for complex authorization rules