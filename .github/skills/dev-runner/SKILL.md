---
name: dev-runner
description: 'Start, stop, or test the Todo AI monorepo. USE FOR: running the FastAPI backend server; running the React Vite frontend dev server; running pytest backend tests; running Vitest frontend tests; starting both servers together; checking if servers are healthy. TRIGGER PHRASES: run backend, start api, start server, run frontend, start web, run dev, run tests, backend tests, frontend tests, pytest, vitest, start the app.'
argument-hint: 'What to run: backend | frontend | both | test-api | test-web | test-all'
---

# Dev Runner

## What This Skill Produces
Starts or tests any part of the Todo AI monorepo using the correct commands, working directories, and environment requirements.

## Monorepo Layout
```
Todo_AI/
├── api/        ← FastAPI backend (Python, uvicorn)
└── web/        ← React + Vite frontend (Node, npm)
```

## When to Use
- "Run the backend" / "Start the API" / "Start the server"
- "Run the frontend" / "Start the web app" / "npm run dev"
- "Start both" / "Run the app" / "Start the dev servers"
- "Run tests" / "Run backend tests" / "Run frontend tests" / "Run all tests"
- "Check if the API is healthy"

---

## Procedure

### 1 — Determine what to run

| User says | Action |
|-----------|--------|
| backend / api / server | [Start Backend](#start-backend) |
| frontend / web / UI | [Start Frontend](#start-frontend) |
| both / app / dev servers | [Start Both](#start-both) |
| test api / pytest / backend tests | [Test Backend](#test-backend) |
| test web / vitest / frontend tests | [Test Frontend](#test-frontend) |
| test all / all tests | [Test Both](#test-all) |

---

### Start Backend

**Pre-flight:** Verify `api/.env` exists with at minimum:
```
DATABASE_URL=mssql+aioodbc://sa:<password>@localhost:1433/TodoDB?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes
CORS_ORIGINS=http://localhost:5173
```
If `.env` is missing, warn the user and stop.

**Command** (run as background terminal from `api/`):
```powershell
cd api; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify:** After starting, hit the health endpoint:
```powershell
Invoke-RestMethod http://localhost:8000/health
```
Expected: `200 OK` with a JSON body confirming status.

**Docs** available at: `http://localhost:8000/api/docs`

---

### Start Frontend

**Pre-flight:** Verify `web/node_modules/` exists. If not, run:
```powershell
cd web; npm install
```

**Command** (run as background terminal from `web/`):
```powershell
cd web; npm run dev
```

**Verify:** The terminal output should show `➜  Local: http://localhost:5173/`.

> `npm run dev` invokes `node ./node_modules/vite/bin/vite.js` — no global Vite required.

---

### Start Both

Run backend first, then frontend. Each in its own background terminal.

1. Follow [Start Backend](#start-backend) steps.
2. Follow [Start Frontend](#start-frontend) steps.
3. Report both URLs:
   - API: `http://localhost:8000/api/docs`
   - Web: `http://localhost:5173`

---

### Test Backend

**Command** (foreground, from `api/`):
```powershell
cd api; pytest
```

- Config: `api/pyproject.toml` sets `asyncio_mode = "auto"` and `testpaths = ["tests"]`.
- Tests use `httpx.AsyncClient` with `ASGITransport` — no live server required.
- Report: pass/fail counts and any tracebacks from stdout.

**Run a single file:**
```powershell
cd api; pytest tests/test_health.py -v
```

---

### Test Frontend

**Command** (foreground, from `web/`):
```powershell
cd web; npm run test
```

- Runs Vitest in `run` mode (single pass, no watch).
- Config: `web/vitest.config.ts`; setup in `web/src/test/setup.ts`.

**Watch mode** (interactive):
```powershell
cd web; npm run test:watch
```

---

### Test All

Run backend tests then frontend tests sequentially:

1. Follow [Test Backend](#test-backend) — report results.
2. Follow [Test Frontend](#test-frontend) — report results.
3. Summarize: total pass/fail for each suite.

---

## Ports & URLs

| Service | Port | URL |
|---------|------|-----|
| FastAPI backend | 8000 | `http://localhost:8000` |
| API docs (Swagger) | 8000 | `http://localhost:8000/api/docs` |
| React frontend | 5173 | `http://localhost:5173` |

---

## Common Issues

| Symptom | Fix |
|---------|-----|
| `ValidationError: DATABASE_URL missing` | Create `api/.env` with `DATABASE_URL` |
| `ModuleNotFoundError` on uvicorn start | Run `pip install -r api/requirements.txt` |
| Frontend blank / network error | Ensure backend is running on port 8000 |
| `npm run dev` fails with permission error | Run `npm install` in `web/` first |
| `ODBC Driver not found` | Install "ODBC Driver 17 for SQL Server" |
