---
id: 2
title: Phase III Security Rules
stage: constitution
date: 2026-02-08
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: Minhal Aslam
command: /sp.constitution
labels: ["security", "authentication", "phase-iii", "jwt", "mcp-tools"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

```text

---

## Authentication & Security Rules

- JWT is mandatory for all chat requests
- Backend must verify JWT on every request
- Frontend identity must never be trusted
- AI agent must never receive secrets
- MCP tools must enforce user ownership

No cross-user data access is permitted under any circumstances.

---

## Frontend Rules (Chat UI)

- Chat UI must use authenticated session
- JWT must be attached automatically
- Conversation must resume after refresh
- UI must reflect backend-confirmed state only
- Errors must be shown clearly but safely

No optimistic updates without backend confirmation.

---

## Data Integrity Rules

- Tasks remain owned by user
- Conversations belong to a single user
- Messages are immutable after creation
- AI responses must be persisted verbatim

---

## Prohibited Actions

- No server-side sessions
- No direct DB access from frontend
- No bypassing MCP tools
- No AI hallucinated task state
- No silent failures

---

## Validation Requirements

Phase III is considered complete
```

## Response snapshot

Constitution updated to version 1.2.0 with Phase III security requirements. Enhanced authentication & security rules with JWT mandate for all chat requests, MCP tools enforcement, and strict user ownership. Added frontend conversation persistence rules, expanded data integrity requirements to cover conversations and messages, and defined prohibited actions. Added validation requirements for Phase III completion criteria.

Key changes:
- Enhanced Authentication & Security Rules with 7 new mandatory requirements
- Updated Frontend Rules to include Chat UI-specific session persistence
- Expanded Data Integrity Assurance with conversation and message immutability
- Added Prohibited Actions section with 5 explicit restrictions
- Added Validation Requirements section defining Phase III completion criteria
- Added formal Governance section with versioning and amendment procedures

## Outcome

- ✅ Impact: Constitution updated from v1.1.0 to v1.2.0 with Phase III security principles
- 🧪 Tests: No tests required for documentation
- 📁 Files: Modified .specify/memory/constitution.md
- 🔁 Next prompts: Implement Phase III features according to updated constitution
- 🧠 Reflection: MINOR version bump appropriate - added new principles without breaking existing governance structure

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation - PASS (all placeholders filled, no unresolved tokens, version coherent)
- Prompt variant (if applicable): Standard constitution update via /sp.constitution
- Next experiment (smallest change to try): Monitor Phase III implementation for any additional security requirements
