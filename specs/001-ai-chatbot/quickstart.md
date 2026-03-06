# Quickstart: Todo AI Chatbot

**Feature**: 001-ai-chatbot
**Date**: 2026-02-08

This guide covers local setup and verification of the AI Chatbot feature.

---

## Prerequisites

### Required Software

- Python 3.11+
- Node.js 18+
- PostgreSQL (or Neon connection)
- Git

### Required API Keys

- **OpenAI API Key**: For AI agent functionality
  - Get from: https://platform.openai.com/api-keys
  - Required model access: `gpt-4` or `gpt-3.5-turbo`

---

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Unix/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create or update `.env` file:

```env
# Database (existing)
DATABASE_URL=postgresql://user:pass@host/dbname

# JWT (existing)
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (NEW for Phase III)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4
```

### 5. Run Database Migrations

```bash
# Apply new conversation and message tables
python -m src.database.init_db
```

### 6. Start Backend Server

```bash
uvicorn main:app --reload --port 8000
```

### 7. Verify Backend

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response: {"status": "healthy"}
```

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment

Create or update `.env.local`:

```env
# API URL (existing)
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Auth URL (existing)
NEXTAUTH_URL=http://localhost:3000
```

### 4. Start Frontend Server

```bash
npm run dev
```

### 5. Verify Frontend

Open http://localhost:3000 in browser. You should see the login page.

---

## End-to-End Verification

### Step 1: Create a Test User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

### Step 2: Login and Get Token

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# Save the returned token
export TOKEN="<returned-jwt-token>"
export USER_ID="<returned-user-id>"
```

### Step 3: Send a Chat Message

```bash
curl -X POST "http://localhost:8000/api/users/${USER_ID}/chat" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task to buy groceries"}'
```

**Expected Response:**
```json
{
  "conversation_id": "uuid-here",
  "message": {
    "id": "uuid-here",
    "role": "assistant",
    "content": "I've created a new task 'buy groceries' for you.",
    "created_at": "2026-02-08T10:30:00Z"
  }
}
```

### Step 4: Verify Task Was Created

```bash
curl "http://localhost:8000/api/users/${USER_ID}/tasks" \
  -H "Authorization: Bearer ${TOKEN}"
```

**Expected:** Task list includes "buy groceries"

### Step 5: Continue the Conversation

```bash
curl -X POST "http://localhost:8000/api/users/${USER_ID}/chat" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What tasks do I have?",
    "conversation_id": "<conversation-id-from-step-3>"
  }'
```

### Step 6: Verify Conversation Persistence

```bash
# List all conversations
curl "http://localhost:8000/api/users/${USER_ID}/conversations" \
  -H "Authorization: Bearer ${TOKEN}"

# Get specific conversation with messages
curl "http://localhost:8000/api/users/${USER_ID}/conversations/<conversation-id>" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

## Frontend Verification

1. Open http://localhost:3000
2. Login with test credentials
3. Navigate to Chat (http://localhost:3000/chat)
4. Send message: "Show me my tasks"
5. Verify response shows the task created via API
6. Refresh page - conversation should persist
7. Try: "Mark buy groceries as complete"
8. Verify task status changes

---

## Validation Checklist

Use this checklist to verify feature completion:

### Backend

- [ ] Chat endpoint accepts messages and returns responses
- [ ] New conversation created when no conversation_id provided
- [ ] Existing conversation continued when conversation_id provided
- [ ] Messages persisted in database
- [ ] AI responses stored verbatim
- [ ] MCP tools correctly create/update/delete tasks
- [ ] JWT authentication enforced on all endpoints
- [ ] User isolation enforced (can't access other users' data)
- [ ] Invalid requests return appropriate error codes

### Frontend

- [ ] Chat page accessible at /chat
- [ ] Unauthenticated users redirected to login
- [ ] Messages display correctly (user on right, assistant on left)
- [ ] Loading state shown while waiting for response
- [ ] Error messages displayed appropriately
- [ ] Conversation persists after page refresh
- [ ] New conversation can be started
- [ ] UI responsive on mobile devices

### Integration

- [ ] Create task via chat → appears in task list
- [ ] Complete task via chat → task marked complete
- [ ] Delete task via chat → task removed
- [ ] List tasks via chat → shows correct tasks
- [ ] Ambiguous requests trigger clarification
- [ ] Non-task requests handled gracefully

---

## Troubleshooting

### "OpenAI API Error"

- Verify `OPENAI_API_KEY` is set correctly
- Check API key has access to required models
- Verify account has sufficient credits

### "Database Connection Error"

- Verify `DATABASE_URL` is correct
- Check database server is running
- Ensure migrations have been applied

### "401 Unauthorized"

- Verify JWT token is valid and not expired
- Check token is passed in Authorization header
- Ensure user_id in URL matches token

### "Conversation Not Found"

- Verify conversation_id exists
- Check conversation belongs to authenticated user
- Ensure correct user_id in URL path

### "MCP Tool Error"

- Check backend logs for detailed error
- Verify task exists (for update/complete/delete)
- Ensure user owns the task being modified

---

## Development Tips

### Viewing Backend Logs

```bash
# Run with debug logging
LOG_LEVEL=DEBUG uvicorn main:app --reload
```

### Testing MCP Tools Directly

```python
# In Python REPL
from backend.src.mcp.tools import create_task, list_tasks

# Test tool execution
result = create_task(user_id="...", title="Test task")
print(result)
```

### Resetting Test Data

```bash
# Delete all conversations and messages
python -c "
from backend.src.database.session import get_session
from backend.src.models.conversation import Conversation
from sqlmodel import delete

with get_session() as session:
    session.exec(delete(Conversation))
    session.commit()
"
```

---

## Next Steps

After verifying the quickstart:

1. Review `spec.md` for complete requirements
2. Run `/sp.tasks` to generate implementation tasks
3. Implement each task following the plan
4. Validate against the checklist above
