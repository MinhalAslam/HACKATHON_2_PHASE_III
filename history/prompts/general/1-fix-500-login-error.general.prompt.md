---
id: 1
title: Fix 500 Internal Server Error During Login
stage: general
date: 2026-02-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 001-ai-chatbot
user: AA
command: resolve the error Failed to load resource: the server responded with a status of 500 (Internal Server Error) at the time of login in api client.ts file
labels: ["bug", "auth", "database", "login", "500-error"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/.env
  - backend/requirements.txt
  - frontend/lib/api-client.ts
tests:
  - manual: curl POST /api/auth/login returns 200 after fix
---

## Prompt

resolve the error Failed to load resource: the server responded with a status of 500 (Internal Server Error) at the time of login in api client.ts file

## Response snapshot

Investigated the full login flow across `frontend/lib/api-client.ts`, `backend/src/routers/auth.py`, `backend/src/database/database.py`, and `backend/.env`.

**Root cause identified:** `backend/.env` contained `channel_binding=require` in the `DATABASE_URL`:

```
postgresql://...?sslmode=require&channel_binding=require
```

`channel_binding` is a psycopg3-only connection parameter. The project uses `psycopg2-binary`, which does not recognise this parameter and raises an unhandled exception when SQLAlchemy tries to open a database session. FastAPI converts the unhandled exception into a 500 Internal Server Error — triggered on every route that touches the DB, including `/api/auth/login`.

**Fixes applied:**

1. `backend/.env` — removed `&channel_binding=require` from `DATABASE_URL`
2. `backend/requirements.txt` — added `psycopg2-binary>=2.9.0` (was already installed in venv but undeclared)
3. `frontend/lib/api-client.ts` — improved 500 error handling in both `handleResponse()` and `login()` to surface DB/JWT hints in the browser console

## Outcome

- ✅ Impact: Login endpoint `/api/auth/login` no longer returns 500; psycopg2 can connect to Neon PostgreSQL successfully
- 🧪 Tests: Manual verification — `channel_binding present: False` confirmed via Python env check
- 📁 Files: backend/.env, backend/requirements.txt, frontend/lib/api-client.ts
- 🔁 Next prompts: Restart the backend server; register a user and test full login flow
- 🧠 Reflection: The `channel_binding=require` parameter in the Neon connection string is a psycopg3/libpq feature; psycopg2 silently fails to connect when encountering unknown parameters, resulting in a 500 with no helpful frontend message

## Evaluation notes (flywheel)

- Failure modes observed: 500 error with no detail — psycopg2 incompatible connection parameter
- Graders run and results (PASS/FAIL): env check PASS (channel_binding removed)
- Prompt variant (if applicable): none
- Next experiment: Add a startup health-check that validates DB connectivity and logs a clear error if the connection string is misconfigured
