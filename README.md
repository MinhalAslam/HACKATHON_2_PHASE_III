# Todo Full-Stack Web Application (Hackathon Phase 2)

This implementation transforms a single-user, in-memory console Todo application into a secure, multi-user, full-stack web application with persistent storage, RESTful APIs, and JWT-based authentication. The application uses Python FastAPI for the backend, Next.js 16+ with App Router for the frontend, SQLModel for ORM, Neon Serverless PostgreSQL for database, and Better Auth for authentication with JWT tokens.

## Architecture Overview

The system follows a microservices-like architecture with clear separation between frontend, backend, and authentication layers:

1. **Frontend Layer** (Next.js 16+):
   - Handles user interface and user experience
   - Manages authentication state using Better Auth
   - Communicates with backend API using JWT tokens in headers
   - Implements responsive design for various screen sizes

2. **Authentication Layer** (Better Auth):
   - Handles user registration and login
   - Issues JWT tokens upon successful authentication
   - Validates credentials and manages user sessions

3. **Backend Layer** (FastAPI + SQLModel):
   - Exposes RESTful API endpoints for task management
   - Validates JWT tokens for all authenticated endpoints
   - Enforces user isolation by checking token identity against URL/user parameters
   - Persists data to Neon PostgreSQL database

4. **Database Layer** (Neon Serverless PostgreSQL):
   - Stores user information and tasks
   - Enforces referential integrity between users and tasks
   - Maintains task ownership and completion states

## Features

- User registration and authentication
- Secure JWT-based authentication
- Task management (create, read, update, delete)
- Task completion toggling
- User isolation - users can only access their own tasks
- Responsive web interface
- Form validation
- Error handling
- Security features (rate limiting, security headers, etc.)

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: Next.js 16+ with App Router
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth (Frontend) + JWT
- **Styling**: Tailwind CSS

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env to include your actual database URL and JWT secret
   ```

5. Initialize the database:
   ```bash
   python -m src.database.init_db
   ```

6. Run the server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file based on `.env.example`:
   ```bash
   cp .env.example .env.local
   # Edit .env.local to match your backend configuration
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

## API Documentation

The API documentation is available at `http://localhost:8000/docs` when the backend is running.

## Security Features

- JWT-based authentication with automatic expiration
- User isolation enforcement at the API level
- Rate limiting to prevent brute force attacks
- Security headers on all responses
- Input validation and sanitization
- Protection against SQL injection and XSS

## Environment Variables

### Backend
- `DATABASE_URL`: Connection string for the PostgreSQL database
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `JWT_ALGORITHM`: Algorithm for JWT encoding (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

### Frontend
- `NEXT_PUBLIC_API_URL`: URL of the backend API
- `NEXTAUTH_URL`: Base URL of the application
- `NEXT_PUBLIC_JWT_SECRET`: Same JWT secret as backend

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.