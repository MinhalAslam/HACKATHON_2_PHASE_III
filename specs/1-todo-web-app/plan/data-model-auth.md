# Data Model: Authentication & API Security (JWT)

## Entity Definitions

### JWT Token (Conceptual - Not Persisted)
**Description**: Authentication token structure for user identification

**Structure**:
- **Header**:
  - alg: String (algorithm used, typically "HS256" or "RS256")
  - typ: String (token type, always "JWT")

- **Payload (Claims)**:
  - sub: String (subject - user identifier, UUID format)
  - exp: Integer (expiration time - Unix timestamp)
  - iat: Integer (issued at time - Unix timestamp)
  - jti: String (JWT ID - optional, for blacklisting)
  - iss: String (issuer - optional, for validation)
  - aud: String (audience - optional, for validation)

**Validation Rules**:
- Token must not be expired (exp > current time)
- Signature must be valid against shared secret
- sub claim must correspond to a valid user in the database
- All required claims must be present

### User Identity Claims (From JWT)
**Description**: User identity information extracted from JWT token

**Fields**:
- `user_id`: UUID (extracted from 'sub' claim)
  - Type: UUID string
  - Constraints: Not Null, References User.id
  - Description: Unique identifier of the authenticated user

- `expires_at`: DateTime
  - Type: Unix timestamp
  - Constraints: Not Null
  - Description: When the token expires

- `issued_at`: DateTime
  - Type: Unix timestamp
  - Constraints: Not Null
  - Description: When the token was issued

**Validation Rules**:
- user_id must correspond to an existing, active user
- expires_at must be in the future
- issued_at should be within reasonable time bounds

### Authentication State (Conceptual)
**Description**: Runtime state for authenticated user requests

**Fields**:
- `user_id`: UUID
  - Type: UUID string
  - Constraints: Not Null
  - Description: ID of the currently authenticated user

- `token_scopes`: Array<String>
  - Type: Array of permission strings
  - Constraints: Optional
  - Description: Permissions granted by this token

- `request_timestamp`: DateTime
  - Type: Unix timestamp
  - Constraints: Not Null
  - Description: When the request was authenticated

**Validation Rules**:
- user_id must match the URL user_id for user-specific operations
- All operations must be authorized for the user's permissions
- State must be refreshed for each request

## Relationships

### User to JWT Claims
- **Relationship Type**: One-to-Many (conceptual)
- **Description**: One user can have many active JWT tokens
- **Implementation**: Tokens are stateless and self-contained, but validate against User table
- **Constraints**:
  - Token user_id must reference valid User.id
  - Validation occurs during each request
  - No persistent relationship stored in database

## Validation Rules

### Business Logic Validation
- Users cannot access resources with user_id different from their token's sub claim
- Expired tokens are rejected regardless of other validity
- Invalid signatures result in immediate rejection
- All authenticated endpoints validate JWT presence and validity

### API Level Validation
- All protected endpoints validate JWT presence in Authorization header
- URL user_id must match the user_id in the JWT token
- Token must be properly formatted as "Bearer <token>"
- Token expiration is validated against server time

### Security Validation
- JWT signature is verified using the shared secret
- Clock skew tolerance is applied (typically ±5 minutes)
- Blacklisted tokens (if using jti) are rejected
- Malformed tokens are rejected with appropriate error messages

## State Transitions

### Token Validation Process
- **Initial State**: Raw token from Authorization header
- **Transition**: Validate structure, signature, and expiration
- **Valid State**: Extracted user identity claims
- **Invalid State**: Return appropriate error (401/403)

### User Access Control
- **Initial State**: Request received at protected endpoint
- **Transition**: Extract JWT, validate, verify user_id match
- **Authorized State**: Grant access to requested resource
- **Unauthorized State**: Return 403 Forbidden

## API Contract Implications

### Protected Endpoints Require:
- Valid Authorization header with "Bearer <token>" format
- Valid JWT token with unexpired, correctly signed claims
- Matching user_id in token and URL parameter
- Sufficient permissions for requested operation

### Error Responses:
- 401 Unauthorized: Missing, invalid, or expired JWT
- 403 Forbidden: Valid JWT but insufficient privileges or user_id mismatch
- 400 Bad Request: Malformed Authorization header or token