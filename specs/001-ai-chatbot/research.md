# Research: Todo AI Chatbot

**Feature**: 001-ai-chatbot
**Date**: 2026-02-08
**Status**: Complete

## Overview

This document captures technology research and decisions for the Phase III AI Chatbot implementation.

---

## 1. MCP (Model Context Protocol) Implementation

### Decision
Use the official `mcp` Python SDK for tool definition with in-process execution.

### Rationale
- **Standardization**: MCP provides a standardized format for tool definitions that AI models can understand
- **Ecosystem compatibility**: Tools defined in MCP format can be reused with any MCP-compatible agent
- **In-process efficiency**: Running tools in-process avoids network overhead and simplifies deployment
- **SQLModel integration**: Direct access to database session for tool execution

### Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| Standalone MCP server | Adds deployment complexity, requires IPC, unnecessary for single-process |
| Custom tool format | Loses ecosystem compatibility, requires custom parsing |
| Direct function calls | Violates constitution requirement for MCP tool usage |

### Implementation Notes
- Install: `pip install mcp`
- Tools registered at application startup
- Each tool receives `user_id` as first parameter for ownership enforcement
- Tool results are JSON-serializable dicts

---

## 2. AI Agent Framework

### Decision
Use OpenAI Agents SDK with function/tool calling capabilities.

### Rationale
- **Native tool support**: Built-in function calling eliminates manual JSON parsing
- **Stateless design**: Agent instance created fresh per request
- **Production ready**: Well-tested in production environments
- **Simple API**: Minimal boilerplate for tool registration

### Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| LangChain | Heavy framework, excessive abstraction for simple use case |
| Raw OpenAI API | Requires manual tool call parsing and loop management |
| Swarm framework | Designed for multi-agent systems, overkill for single agent |
| Anthropic Claude | Would work but OpenAI specified in requirements |

### Implementation Notes
- Install: `pip install openai`
- Agent configured with system prompt at creation
- Tools passed as function definitions
- Response includes both text and tool call results

---

## 3. Conversation Persistence Strategy

### Decision
Full conversation reconstruction from database on each request with token-based truncation.

### Rationale
- **Stateless compliance**: No server-side session storage required
- **Simplicity**: Single query to reconstruct context
- **Reliability**: Database is source of truth, survives restarts
- **Token management**: Prevents context overflow in long conversations

### Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| Sliding window only | May lose important early context |
| Message summarization | Adds complexity, may lose accuracy |
| Redis session cache | Violates no server-side sessions requirement |
| Client-side storage | Cannot enforce data integrity |

### Implementation Notes
- Query: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC`
- Token counting: Use `tiktoken` library for accurate counts
- Truncation: Remove oldest messages first, keep recent context
- Max context: ~4000 tokens for messages (leaving room for system prompt and response)

---

## 4. Database Schema Design

### Decision
Two new tables: `conversation` and `message` with foreign key relationships.

### Rationale
- **Normalization**: Separate tables for conversations and messages
- **User isolation**: `user_id` on conversation enables ownership queries
- **Immutability**: Messages have no `updated_at` column, enforcing immutability
- **Indexing**: Foreign keys indexed for efficient joins

### Schema Summary

```sql
-- Conversation table
CREATE TABLE conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_conversation_user_id ON conversation(user_id);

-- Message table
CREATE TABLE message (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_message_conversation_id ON message(conversation_id);
```

---

## 5. Frontend Chat UI Approach

### Decision
Custom React components following existing project patterns.

### Rationale
- **Consistency**: Matches existing frontend component structure
- **Simplicity**: No additional UI library dependencies
- **Control**: Full control over styling and behavior
- **Integration**: Works with existing auth and API patterns

### Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| ChatKit library | Additional dependency, may conflict with existing styles |
| Vercel AI SDK | Designed for streaming, adds complexity for simple chat |
| Pre-built chat widget | Less control, harder to integrate with existing auth |

### Implementation Notes
- Components: `ChatContainer`, `MessageList`, `MessageInput`, `ChatMessage`
- State: Managed with React hooks (useState, useEffect)
- API: Fetch-based calls to chat endpoint
- Auth: JWT attached via existing API client interceptor

---

## 6. Error Handling Strategy

### Decision
Three-tier error handling with graceful degradation.

### Tiers

1. **MCP Tool Level**
   - Return structured error in result, never throw
   - Format: `{ success: false, error: "message" }`
   - Agent interprets and responds appropriately

2. **Agent Level**
   - Catch tool errors, generate user-friendly response
   - Never expose internal details
   - Maintain conversation flow

3. **API Level**
   - Catch agent failures (API errors, timeouts)
   - Return HTTP 500 with generic message
   - Log full error for debugging

### Rationale
- Agent can handle tool failures intelligently
- User never sees raw exceptions
- System remains secure (no internal detail leakage)
- Debugging enabled via server logs

---

## Dependencies Summary

### Backend (add to requirements.txt)
```
# AI/Agent dependencies (NEW for Phase III)
openai>=1.0.0
tiktoken>=0.5.0

# Existing dependencies (already installed)
# fastapi==0.104.1
# uvicorn[standard]==0.24.0
# sqlmodel==0.0.16
# pydantic==2.5.0
# PyJWT==2.8.0
# python-dotenv==1.0.0
```

### Frontend (existing dependencies sufficient)
- React 19.2.3 (via Next.js 16.1.6) - existing
- Tailwind CSS 4 - existing
- No additional packages needed

### Environment Variables (add to .env)
```
# OpenAI API (NEW)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Existing variables (already configured)
# DATABASE_URL=postgresql://...
# JWT_SECRET_KEY=...
# JWT_ALGORITHM=HS256
```

---

## Open Items

None - all research questions resolved.

---

## Integration Notes

### Reusing Existing Patterns

1. **TaskService Pattern**: MCP tools should instantiate `TaskService(session)` and call its methods
2. **JWT Verification**: Reuse `verify_url_user_id_matches_token()` from `src/utils/auth.py`
3. **API Client Pattern**: Extend existing `apiClient` object in `lib/api-client.ts` with chat methods
4. **Component Style**: Follow existing Tailwind patterns from TaskList.tsx, TaskItem.tsx

### Database Considerations

- Use existing `get_session()` generator from `src/database/database.py`
- New models extend SQLModel like existing Task/User models
- NullPool already configured for serverless PostgreSQL
