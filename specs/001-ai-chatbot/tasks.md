# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/001-ai-chatbot/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested in specification. Manual validation per quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/app/`, `frontend/components/`, `frontend/lib/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add new dependencies and create package structure for Phase III

- [x] T001 Add OpenAI SDK dependency to backend/requirements.txt: `openai>=1.0.0`
- [x] T002 Add tiktoken dependency to backend/requirements.txt: `tiktoken>=0.5.0`
- [x] T003 [P] Create MCP package directory structure in backend/src/mcp/__init__.py
- [x] T004 [P] Create agent package directory structure in backend/src/agent/__init__.py
- [x] T005 [P] Create chat components directory in frontend/components/chat/ (empty index file)
- [x] T006 Add OPENAI_API_KEY and OPENAI_MODEL to backend/.env.example

**Checkpoint**: Package structure ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database models and MCP tools that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models

- [x] T007 [P] Create Conversation model in backend/src/models/conversation.py with fields: id (UUID PK), user_id (FK to User), title (Optional str), created_at, updated_at per data-model.md
- [x] T008 [P] Create Message model in backend/src/models/message.py with fields: id (UUID PK), conversation_id (FK), role (Enum: user/assistant), content (str), created_at per data-model.md
- [x] T009 Update backend/src/models/__init__.py to export Conversation, Message, ConversationRead, MessageRead
- [x] T010 Add conversations relationship to User model in backend/src/models/user.py: `conversations: List["Conversation"] = Relationship(back_populates="user")`
- [x] T011 Run database migration to create conversation and message tables (python -m src.database.init_db)

### MCP Tools (All tools needed for any user story)

- [x] T012 Create MCP tool registry in backend/src/mcp/server.py with tool registration function
- [x] T013 [P] Implement create_task MCP tool in backend/src/mcp/tools.py: accepts user_id, title, description; uses TaskService; returns {success: bool, task: dict, error?: str}
- [x] T014 [P] Implement list_tasks MCP tool in backend/src/mcp/tools.py: accepts user_id, status (optional); uses TaskService; returns {success: bool, tasks: list, error?: str}
- [x] T015 [P] Implement get_task MCP tool in backend/src/mcp/tools.py: accepts user_id, task_id or title_search; returns single task or matches
- [x] T016 [P] Implement update_task MCP tool in backend/src/mcp/tools.py: accepts user_id, task_id, title?, description?; uses TaskService
- [x] T017 [P] Implement complete_task MCP tool in backend/src/mcp/tools.py: accepts user_id, task_id; toggles completed status
- [x] T018 [P] Implement delete_task MCP tool in backend/src/mcp/tools.py: accepts user_id, task_id; uses TaskService.delete_task

### AI Agent Configuration

- [x] T019 Create agent configuration in backend/src/agent/config.py with OPENAI_API_KEY, MODEL, system prompt from plan.md
- [x] T020 Create task agent runner in backend/src/agent/task_agent.py: initializes OpenAI client, registers MCP tools as functions, implements run_agent(messages, user_id) -> response

### Chat Service Foundation

- [x] T021 Create ChatService class in backend/src/services/chat_service.py with methods: create_conversation, get_conversation, list_conversations, add_message, get_messages

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create Task via Chat (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks through natural language chat messages

**Independent Test**: Send "Add a task to buy groceries" and verify task appears in /tasks page

### Backend Implementation

- [x] T022 [US1] Create chat router in backend/src/routers/chat.py with POST /api/{user_id}/chat endpoint
- [x] T023 [US1] Implement chat endpoint logic: validate JWT, verify user_id matches token, create/get conversation, store user message, call agent, store assistant response, return ChatResponse
- [x] T024 [US1] Add chat router to backend/main.py: `app.include_router(chat.router, prefix="/api/{user_id}", tags=["chat"])`

### Frontend Implementation

- [x] T025 [P] [US1] Create ChatMessage component in frontend/components/chat/ChatMessage.tsx: displays single message with user/assistant styling (user: right-aligned blue, assistant: left-aligned gray)
- [x] T026 [P] [US1] Create MessageInput component in frontend/components/chat/MessageInput.tsx: text input with send button, onSubmit callback
- [x] T027 [US1] Create MessageList component in frontend/components/chat/MessageList.tsx: scrollable container rendering ChatMessage components, auto-scroll to bottom
- [x] T028 [US1] Create ChatContainer component in frontend/components/chat/ChatContainer.tsx: manages conversation state, calls sendMessage API, renders MessageList and MessageInput
- [x] T029 [US1] Create chat page in frontend/app/chat/page.tsx: authenticated route, renders ChatContainer, handles loading/error states
- [x] T030 [US1] Add sendMessage function to frontend/lib/api-client.ts: POST /api/{user_id}/chat with message and optional conversation_id
- [x] T031 [US1] Add Chat link to Header component in frontend/components/Header.tsx: navigation to /chat

**Checkpoint**: User Story 1 complete - users can create tasks via chat

---

## Phase 4: User Story 2 - List and Query Tasks (Priority: P2)

**Goal**: Users can ask chatbot to show their tasks with filtering

**Independent Test**: Ask "What are my tasks?" and verify chatbot lists all user tasks

### Implementation (Agent already has list_tasks tool from Phase 2)

- [x] T032 [US2] Verify list_tasks tool handles empty task list gracefully in backend/src/mcp/tools.py
- [x] T033 [US2] Verify list_tasks tool supports status filter (completed/incomplete) in backend/src/mcp/tools.py
- [x] T034 [US2] Test agent correctly invokes list_tasks for queries like "show my tasks", "what tasks do I have"

**Checkpoint**: User Story 2 complete - users can list and query tasks via chat

---

## Phase 5: User Story 3 - Complete and Update Tasks (Priority: P3)

**Goal**: Users can mark tasks complete or update details via chat

**Independent Test**: Say "Mark buy groceries as done" and verify task shows as completed

### Implementation (Agent already has complete_task and update_task tools from Phase 2)

- [x] T035 [US3] Verify complete_task tool returns confirmation message in backend/src/mcp/tools.py
- [x] T036 [US3] Verify update_task tool handles partial updates (title only, description only) in backend/src/mcp/tools.py
- [x] T037 [US3] Verify get_task tool can find tasks by partial title match for disambiguation in backend/src/mcp/tools.py
- [x] T038 [US3] Test agent handles ambiguous requests by listing matches and asking for clarification

**Checkpoint**: User Story 3 complete - users can complete and update tasks via chat

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Users can delete tasks through natural language

**Independent Test**: Say "Delete the groceries task" and verify task is removed

### Implementation (Agent already has delete_task tool from Phase 2)

- [x] T039 [US4] Verify delete_task tool returns confirmation message in backend/src/mcp/tools.py
- [x] T040 [US4] Verify delete_task tool handles non-existent task gracefully in backend/src/mcp/tools.py
- [x] T041 [US4] Test agent confirms deletion before executing (optional safety check)

**Checkpoint**: User Story 4 complete - users can delete tasks via chat

---

## Phase 7: User Story 5 - Conversation Persistence (Priority: P5)

**Goal**: Chat history persists across page refreshes and sessions

**Independent Test**: Have a conversation, refresh page, verify history is displayed

### Backend Implementation

- [x] T042 [US5] Add GET /api/{user_id}/conversations endpoint to backend/src/routers/chat.py: lists user's conversations
- [x] T043 [US5] Add GET /api/{user_id}/conversations/{conversation_id} endpoint to backend/src/routers/chat.py: returns conversation with messages
- [x] T044 [US5] Add DELETE /api/{user_id}/conversations/{conversation_id} endpoint to backend/src/routers/chat.py: deletes conversation

### Frontend Implementation

- [x] T045 [US5] Add getConversations function to frontend/lib/api-client.ts: GET /api/{user_id}/conversations
- [x] T046 [US5] Add getConversation function to frontend/lib/api-client.ts: GET /api/{user_id}/conversations/{id}
- [x] T047 [US5] Update ChatContainer in frontend/components/chat/ChatContainer.tsx to load existing conversation on mount
- [x] T048 [US5] Store conversation_id in component state, persist across messages in frontend/components/chat/ChatContainer.tsx

**Checkpoint**: User Story 5 complete - conversations persist across refreshes

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T049 Verify JWT authentication enforced on all chat endpoints in backend/src/routers/chat.py
- [x] T050 Verify user isolation: test that user A cannot access user B's conversations
- [x] T051 Verify error messages are user-friendly, no system details exposed
- [x] T052 Verify agent rejects non-task-related requests politely
- [x] T053 Run quickstart.md end-to-end validation
- [x] T054 Update project README.md with Phase III chat feature documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3-7 (User Stories)**: All depend on Phase 2 completion
  - US1 (P1) → US2 (P2) → US3 (P3) → US4 (P4) → US5 (P5) in priority order
  - OR can be parallelized if team capacity allows
- **Phase 8 (Polish)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (Create Task)**: Foundational only - MVP story, no dependencies on other stories
- **US2 (List Tasks)**: Foundational only - can run parallel to US1
- **US3 (Complete/Update)**: Foundational only - can run parallel to US1, US2
- **US4 (Delete Tasks)**: Foundational only - can run parallel to US1-3
- **US5 (Persistence)**: Foundational only - can run parallel to US1-4, but best after US1

### Within Each Phase

- Tasks marked [P] can run in parallel
- Models before services (T007-T008 before T021)
- Backend before frontend within each story
- Services before routers (T021 before T022)

---

## Parallel Execution Examples

### Phase 2: Foundational (Maximum Parallelism)

```
Parallel Group A (Models):
  T007: Conversation model
  T008: Message model

Sequential (after A):
  T009: Export models
  T010: User relationship
  T011: Migration

Parallel Group B (MCP Tools - after T011):
  T013: create_task tool
  T014: list_tasks tool
  T015: get_task tool
  T016: update_task tool
  T017: complete_task tool
  T018: delete_task tool

Sequential (after B):
  T019: Agent config
  T020: Agent runner
  T021: Chat service
```

### Phase 3: User Story 1 (Frontend Parallelism)

```
Sequential (Backend):
  T022: Chat router
  T023: Chat endpoint logic
  T024: Register router

Parallel Group (Frontend Components):
  T025: ChatMessage component
  T026: MessageInput component

Sequential (after parallel):
  T027: MessageList
  T028: ChatContainer
  T029: Chat page
  T030: API client method
  T031: Header link
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (6 tasks)
2. Complete Phase 2: Foundational (15 tasks)
3. Complete Phase 3: User Story 1 (10 tasks)
4. **STOP and VALIDATE**: Test "Add a task to buy groceries"
5. Deploy/demo if ready - MVP complete!

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → MVP: Create tasks via chat
3. Add User Story 2 → List/query tasks via chat
4. Add User Story 3 → Complete/update tasks via chat
5. Add User Story 4 → Delete tasks via chat
6. Add User Story 5 → Conversation persistence
7. Polish → Production ready

---

## Task Summary

| Phase | Story | Task Count | Parallel Opportunities |
|-------|-------|------------|----------------------|
| Phase 1 | Setup | 6 | 3 parallel (T003, T004, T005) |
| Phase 2 | Foundational | 15 | 8 parallel (T007-T008, T013-T018) |
| Phase 3 | US1 - Create Task | 10 | 2 parallel (T025, T026) |
| Phase 4 | US2 - List Tasks | 3 | 0 |
| Phase 5 | US3 - Complete/Update | 4 | 0 |
| Phase 6 | US4 - Delete Tasks | 3 | 0 |
| Phase 7 | US5 - Persistence | 7 | 0 |
| Phase 8 | Polish | 6 | 0 |
| **Total** | | **54** | **13 parallel** |

---

## Notes

- All tasks include exact file paths for LLM execution
- No tests generated (not requested in spec)
- Each user story independently testable after completion
- MCP tools created in Foundational phase serve all stories
- Frontend components follow existing Tailwind patterns
- Commit after each task or logical group
