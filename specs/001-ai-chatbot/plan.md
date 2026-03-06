# Implementation Plan: Todo AI Chatbot

**Branch**: `001-ai-chatbot` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-chatbot/spec.md`

## Summary

Build an AI-powered chatbot that allows users to manage todos using natural language. The chatbot operates through a stateless request cycle, uses MCP tools for all task operations, persists conversations and messages in the database, and integrates with the existing FastAPI backend and Next.js frontend while enforcing JWT authentication and user isolation.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript/Next.js 16.1.6 (Frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.104.1, SQLModel 0.0.16, PyJWT 2.8.0, OpenAI SDK, MCP Python SDK
- Frontend: Next.js 16.1.6, React 19.2.3, Tailwind CSS 4
**Storage**: PostgreSQL (Neon Serverless) with SQLModel ORM, NullPool for serverless
**Testing**: pytest (backend), manual validation per spec
**Target Platform**: Web application (Linux server backend, browser frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <3s response time (p95), 100+ concurrent chat sessions
**Constraints**: Stateless operations, no streaming, no server-side sessions
**Scale/Scope**: Same user base as existing todo app, single conversation per user initially

## Existing Codebase Analysis

### Backend Structure (Reviewed)
```
backend/
├── main.py                      # FastAPI app with CORS, security middleware
├── src/
│   ├── database/
│   │   ├── database.py          # SQLModel engine with NullPool (serverless)
│   │   ├── session.py           # Session management
│   │   └── init_db.py           # Table creation
│   ├── models/
│   │   ├── user.py              # User model (UUID pk, email, hashed_password, role)
│   │   └── task.py              # Task model (UUID pk, title, description, completed, user_id FK)
│   ├── services/
│   │   └── task_service.py      # TaskService class with CRUD operations
│   ├── routers/
│   │   ├── auth.py              # /api/auth/* endpoints
│   │   └── tasks.py             # /api/{user_id}/tasks/* endpoints
│   ├── middleware/
│   │   ├── security.py          # Security headers middleware
│   │   └── rate_limit.py        # Rate limiting
│   └── utils/
│       ├── jwt.py               # JWT create/verify (PyJWT)
│       ├── auth.py              # get_current_user, verify_url_user_id_matches_token
│       └── logger.py            # Logging setup
```

### Frontend Structure (Reviewed)
```
frontend/
├── app/
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page
│   ├── login/page.tsx           # Login page
│   ├── signup/page.tsx          # Signup page
│   └── tasks/page.tsx           # Tasks page (main authenticated view)
├── components/
│   ├── AuthForm.tsx             # Login/signup form
│   ├── Header.tsx               # App header
│   ├── Footer.tsx               # App footer
│   ├── TaskList.tsx             # Task list component
│   ├── TaskItem.tsx             # Individual task
│   ├── TaskForm.tsx             # Create/edit task form
│   ├── LoadingSpinner.tsx       # Loading state
│   └── ErrorMessage.tsx         # Error display
└── lib/
    └── api-client.ts            # Centralized API client with JWT auto-attach
```

### Key Integration Points
- **JWT Auth**: Token stored in localStorage, auto-attached via `getAuthHeaders()` in api-client.ts
- **User ID Pattern**: Routes use `/api/{user_id}/...` with `verify_url_user_id_matches_token()`
- **Task Service**: `TaskService` class pattern - reusable for MCP tools
- **Database**: SQLModel with PostgreSQL, NullPool for serverless connections

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| Spec-First Development | ✅ PASS | spec.md completed with 15 functional requirements |
| Security-by-Design | ✅ PASS | JWT mandatory for chat, user isolation enforced, MCP tools verify ownership |
| Agentic Development Compliance | ✅ PASS | Following Spec → Plan → Tasks → Implement workflow |
| API-First Design | ✅ PASS | RESTful chat endpoint with JWT auth, contracts defined |
| Data Integrity Assurance | ✅ PASS | Conversations/Messages persisted in PostgreSQL, messages immutable |
| Production Realism | ✅ PASS | Real database, real auth, real AI integration |
| JWT mandatory for chat | ✅ PASS | All chat requests require valid JWT |
| MCP tools enforce ownership | ✅ PASS | User ID passed to all MCP tools, validated before execution |
| No server-side sessions | ✅ PASS | Stateless design, context reconstructed from DB per request |
| No bypassing MCP tools | ✅ PASS | AI agent only invokes tools, no direct DB access |
| Messages immutable | ✅ PASS | No update/delete endpoints for messages |
| Conversation resumes after refresh | ✅ PASS | History loaded from DB on frontend mount |

**Gate Status**: ✅ ALL GATES PASSED

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Local setup guide
├── contracts/           # Phase 1: API specifications
│   └── chat-api.yaml    # OpenAPI spec for chat endpoint
└── tasks.md             # Phase 2: Implementation tasks
```

### New Files to Create (Phase III)

```text
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py   # NEW: Conversation model (user_id FK, title, timestamps)
│   │   └── message.py        # NEW: Message model (conversation_id FK, role, content)
│   ├── services/
│   │   └── chat_service.py   # NEW: Chat orchestration service
│   ├── routers/
│   │   └── chat.py           # NEW: /api/{user_id}/chat, /api/{user_id}/conversations
│   ├── mcp/
│   │   ├── __init__.py       # NEW: MCP package init
│   │   ├── server.py         # NEW: MCP server/tool registry
│   │   └── tools.py          # NEW: create_task, list_tasks, update_task, complete_task, delete_task
│   └── agent/
│       ├── __init__.py       # NEW: Agent package init
│       ├── config.py         # NEW: OpenAI config, system prompt
│       └── task_agent.py     # NEW: Agent runner with tool invocation

frontend/
├── app/
│   └── chat/
│       └── page.tsx          # NEW: Chat page (authenticated)
├── components/
│   └── chat/
│       ├── ChatContainer.tsx # NEW: Main chat wrapper with state
│       ├── MessageList.tsx   # NEW: Scrollable message display
│       ├── MessageInput.tsx  # NEW: Input field with send button
│       └── ChatMessage.tsx   # NEW: Single message bubble (user/assistant styling)
└── lib/
    └── chat-api.ts           # NEW: sendMessage(), getConversations(), getConversation()
```

### Files to Modify (Minimal Changes)

```text
backend/
├── main.py                   # ADD: include chat router
├── src/models/__init__.py    # ADD: export Conversation, Message
└── src/models/user.py        # ADD: conversations relationship

frontend/
├── components/Header.tsx     # ADD: Chat navigation link
└── lib/api-client.ts         # ADD: chat API methods to apiClient object
```

**Structure Decision**: Web application structure using existing backend/ and frontend/ directories. New chat functionality added as additional modules without modifying existing task management code.

## Complexity Tracking

No constitution violations requiring justification. Design adheres to all principles.

---

## Phase 0: Research Decisions

### Decision 1: MCP Server Implementation

**Decision**: Use `mcp` Python SDK with in-process tool execution

**Rationale**:
- Official MCP SDK provides standardized tool definition format
- In-process execution avoids network overhead for local tool calls
- Tools can directly access SQLModel session for database operations
- Maintains stateless design - no persistent MCP server process

**Alternatives Considered**:
- Standalone MCP server process: Rejected - adds deployment complexity, requires IPC
- Custom tool format: Rejected - loses compatibility with MCP ecosystem
- Direct function calls without MCP: Rejected - violates constitution requirement

### Decision 2: AI Agent Framework

**Decision**: Use OpenAI Agents SDK with function calling

**Rationale**:
- Native support for tool/function calling
- Stateless by design - agent created per request
- Clear separation between conversation and tool execution
- Well-documented patterns for task management domains

**Alternatives Considered**:
- LangChain agents: Rejected - heavier framework, more complexity than needed
- Raw OpenAI API: Rejected - requires manual tool call parsing
- Swarm framework: Rejected - designed for multi-agent, overkill for single agent

### Decision 3: Conversation Reconstruction Strategy

**Decision**: Load full conversation history on each request, truncate oldest messages if exceeding token limit

**Rationale**:
- Maintains stateless backend - no session storage
- Simple implementation - query by conversation_id, order by timestamp
- Token management prevents context overflow
- Preserves recent context which is most relevant for task operations

**Alternatives Considered**:
- Sliding window only: Rejected - loses important context
- Summarization: Rejected - adds complexity, may lose accuracy
- External memory store: Rejected - violates simplicity constraint

### Decision 4: Tool Naming Convention

**Decision**: Use verb_noun format matching task operations

**Tools**:
- `create_task` - Create a new task
- `list_tasks` - Get all user's tasks
- `get_task` - Get single task by ID or title match
- `update_task` - Modify task title/description
- `complete_task` - Mark task as complete
- `delete_task` - Remove a task

**Rationale**:
- Clear, action-oriented names
- Maps directly to spec functional requirements
- Consistent with existing task_service patterns

### Decision 5: Error Handling Boundaries

**Decision**: Three-tier error handling

1. **MCP Tool Level**: Return structured error in tool result, never throw
2. **Agent Level**: Interpret tool errors, generate user-friendly response
3. **API Level**: Catch agent failures, return 500 with safe error message

**Rationale**:
- Agent can recover from tool errors gracefully
- User never sees raw exceptions or system details
- Maintains constitution requirement for clear error messages

---

## Phase 1: Design Artifacts

### Entities (see data-model.md for full details)

**Conversation**
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to User, indexed)
- `title`: Optional[str] - Auto-generated or user-provided
- `created_at`: datetime
- `updated_at`: datetime

**Message**
- `id`: UUID (primary key)
- `conversation_id`: UUID (foreign key to Conversation, indexed)
- `role`: Enum["user", "assistant"]
- `content`: str (text of message)
- `created_at`: datetime
- Immutable after creation - no update_at field

### API Contracts (see contracts/chat-api.yaml)

**POST /api/users/{user_id}/chat**
- Creates or continues conversation
- Accepts: `{ message: string, conversation_id?: uuid }`
- Returns: `{ conversation_id: uuid, message: MessageResponse }`
- Auth: JWT required, user_id must match token

**GET /api/users/{user_id}/conversations**
- Lists user's conversations
- Returns: `{ conversations: ConversationSummary[] }`
- Auth: JWT required

**GET /api/users/{user_id}/conversations/{conversation_id}**
- Gets conversation with messages
- Returns: `{ conversation: Conversation, messages: Message[] }`
- Auth: JWT required, user must own conversation

### Agent System Prompt

```
You are a helpful task management assistant. You help users manage their todo list through natural conversation.

You have access to the following tools:
- create_task: Create a new task with a title
- list_tasks: Show all tasks or filter by completion status
- get_task: Find a specific task by name
- update_task: Change a task's title or description
- complete_task: Mark a task as done
- delete_task: Remove a task

Rules:
1. Only perform task-related operations. Politely decline other requests.
2. Always confirm after making changes (created, updated, deleted, completed).
3. If a request is ambiguous, ask for clarification.
4. When multiple tasks match, list them and ask which one.
5. Be concise but friendly in responses.
6. Never expose internal IDs or system details to users.
```

---

## Implementation Phases

### Phase 3.1: Database Foundation
- Create Conversation model with user relationship
- Create Message model with conversation relationship
- Add database migrations
- Validate referential integrity

### Phase 3.2: MCP Server Implementation
- Initialize MCP tool registry
- Implement 6 task tools with user scoping
- Add error handling and validation
- Test tools in isolation

### Phase 3.3: AI Agent Integration
- Configure OpenAI client
- Define system prompt and behavior
- Register MCP tools with agent
- Implement tool invocation flow

### Phase 3.4: Chat API Endpoint
- Create chat router
- Implement POST /chat endpoint
- Add conversation CRUD endpoints
- Integrate with existing JWT auth

### Phase 3.5: Frontend Chat UI
- Create chat page component
- Implement message list and input
- Connect to chat API
- Handle loading and error states

---

## Validation Checklist

- [ ] Conversations persist across server restarts
- [ ] Messages are immutable (no edit/delete endpoints)
- [ ] MCP tools verify user ownership before execution
- [ ] Agent never accesses tasks directly (only via tools)
- [ ] JWT required on all chat endpoints
- [ ] User cannot access other users' conversations
- [ ] Frontend loads conversation history on mount
- [ ] Error messages are user-friendly, no system details exposed
- [ ] Response time < 3 seconds for simple operations
- [ ] No server-side session state

---

## Architectural Decisions Detected

📋 **Architectural decision detected**: MCP tool design and naming conventions
- Document reasoning and tradeoffs? Run `/sp.adr mcp-tool-design`

📋 **Architectural decision detected**: Stateless conversation reconstruction
- Document reasoning and tradeoffs? Run `/sp.adr conversation-state-management`

📋 **Architectural decision detected**: Agent framework selection (OpenAI Agents SDK)
- Document reasoning and tradeoffs? Run `/sp.adr agent-framework-selection`
