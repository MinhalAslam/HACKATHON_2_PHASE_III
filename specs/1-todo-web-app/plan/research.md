# Research Summary: Todo Full-Stack Web Application (Hackathon Phase 2)

## Decision Log

### 1. JWT Verification Approach in FastAPI

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

### 2. JWT Claim Structure for User Identity

**Decision**: Using 'sub' (subject) claim for user ID and 'exp' for expiration

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

### 3. URL User_ID Matching Strategy

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

### 4. Database Schema Design for User-Task Relationship

**Decision**: Foreign key relationship between Task and User tables with SQLModel

**Rationale**:
- Enforces data integrity at the database level
- Enables efficient querying with joins when needed
- Follows relational database best practices
- Ensures referential integrity between users and their tasks

**Alternatives considered**:
- Storing user ID as a field without foreign key: Removes database-level protection against orphaned records
- Separate tables per user: Complex and doesn't scale well with many users

**Schema structure**:
- User table with primary key (UUID)
- Task table with foreign key to User
- Proper indexing on user_id for efficient queries

### 5. Error Handling and HTTP Status Codes

**Decision**: Standard HTTP status codes (200, 201, 401, 403, 404, 500) with descriptive error messages

**Rationale**:
- Follows REST API best practices
- Provides clear communication about request outcomes
- Compatible with frontend error handling patterns
- Standardized and understood by API consumers

**Status codes mapping**:
- 200: Successful GET, PUT, PATCH requests
- 201: Successful POST requests
- 204: Successful DELETE requests
- 400: Bad Request (malformed request, validation errors)
- 401: Unauthorized (missing or invalid JWT)
- 403: Forbidden (user trying to access others' resources)
- 404: Not Found (resource doesn't exist)
- 500: Internal Server Error (unexpected server issues)

**Alternatives considered**:
- Custom error codes: Non-standard and harder to integrate with existing tools
- Generic error responses: Insufficient information for clients to handle errors appropriately

### 6. Frontend API Client Structure

**Decision**: Centralized API client with automatic JWT token injection

**Rationale**:
- Provides single source of truth for API interactions
- Handles authentication transparently for all requests
- Reduces code repetition across components
- Makes error handling consistent across the application

**Implementation approach**:
- Create a service module that encapsulates all API calls
- Include token management and injection
- Handle common error cases consistently
- Support both authenticated and public endpoints

**Alternatives considered**:
- Dispersed API calls: Repetitive, harder to maintain, inconsistent authentication handling
- Per-component API logic: Leads to inconsistency in error handling and authentication

### 7. Environment Variable Management for JWT Secret

**Decision**: Using environment variables loaded at application startup

**Rationale**:
- Secure way to manage secrets without hardcoding
- Separates configuration from code
- Aligns with 12-factor app methodology
- Allows for different secrets in different environments (dev, staging, prod)

**Implementation approach**:
- Use python-dotenv for backend to load from .env files
- Use NEXT_PUBLIC_ prefixed variables for Next.js environment variables
- Validate that required environment variables exist at startup

**Alternatives considered**:
- Hardcoded secrets: Major security risk, especially with version control
- Configuration files: Risk of accidental commits with sensitive information

### 8. FastAPI Security Dependency Pattern

**Decision**: Using Depends() with a security function that validates JWT

**Rationale**:
- Leverages FastAPI's built-in dependency injection
- Clean separation between authentication and business logic
- Automatic documentation of required authentication
- Easy to test and maintain

**Implementation pattern**:
```python
def get_current_user(token: str = Security(HTTPBearer())) -> User:
    # Verify JWT and extract user info
    # Return user object or raise HTTPException
```

### 9. Next.js Authentication State Management

**Decision**: Using NextAuth.js with custom JWT handling

**Rationale**:
- Well-established authentication solution for Next.js
- Good integration with Better Auth
- Handles session management and token refresh
- Provides hooks for protecting routes

**Alternatives considered**:
- Custom authentication provider: Would require implementing more security measures from scratch
- Multiple authentication libraries: Could lead to conflicts and maintenance issues

### 10. SQLModel Model Design for Data Consistency

**Decision**: Using SQLModel's base class for consistent database models

**Rationale**:
- Provides Pydantic validation alongside SQLAlchemy ORM
- Consistent model structure between request/response and database models
- Type safety for database operations
- Good integration with FastAPI for request/response validation

**Model patterns**:
- Base models with common fields (id, timestamps)
- Separate models for request/response validation
- Proper typing for all fields