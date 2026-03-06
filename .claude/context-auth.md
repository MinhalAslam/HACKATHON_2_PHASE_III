<!-- TECH_START: Authentication & API Security -->

## Technologies for Authentication & API Security (JWT)

### Backend Authentication Technologies:
- PyJWT: For handling JWT token creation and verification
- python-jose: For JWT encoding/decoding and cryptographic operations
- FastAPI Security: For HTTP authentication schemes and dependency management
- HTTP Bearer: Standard for sending JWT in Authorization header

### Frontend Authentication Technologies:
- Better Auth: Authentication library for handling user login/registration
- Browser Storage: For storing JWT tokens (localStorage/sessionStorage)
- Frontend Security: Techniques to protect JWT tokens from XSS attacks

### Security & Authentication:
- JWT (JSON Web Tokens): For authentication between frontend and backend
- Bearer Authentication: Standard for sending JWT in Authorization header
- Shared Secret: For signing and verifying JWT tokens
- Token Validation: Process of verifying JWT signature and expiration

### API Security Design:
- Stateless Authentication: No server-side session storage
- User Isolation: Ensuring users can only access their own resources
- Authorization Checks: Validating user permissions before granting access
- URL Parameter Validation: Matching JWT user_id with URL user_id

<!-- TECH_END: Authentication & API Security -->