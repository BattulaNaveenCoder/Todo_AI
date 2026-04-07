---
name: test-runner
description: "Auto-triggered when asked to run tests. Detects context (backend or frontend), runs the correct test suite, and reports results with suggested fixes for failures. TRIGGER PHRASES: run tests, run the tests, run pytest, run vitest, check tests, are tests passing, test results."
---

# Test Runner

## What This Skill Produces
Detects which test suite to run (backend or frontend), executes it with the correct command, and reports pass/fail results with concrete fix suggestions for any failures.

## Detection Rules

Run **BACKEND** tests if:
- User is working in `/api` or mentions Python / backend / pytest
- Changed files are in `api/`

Run **FRONTEND** tests if:
- User is working in `/web` or mentions React / TypeScript / vitest
- Changed files are in `web/`

If unclear, ask: _"Should I run backend tests (pytest) or frontend tests (vitest)?"_

---

## Backend Test Execution

**Command** (foreground, from `api/`):
```powershell
cd api; pytest -v --tb=short
```

**With coverage:**
```powershell
cd api; pytest --cov=app --cov-report=term-missing -v
```

**Single file:**
```powershell
cd api; pytest tests/test_health.py -v
```

- Config: `api/pyproject.toml` — `asyncio_mode = "auto"`, `testpaths = ["tests"]`
- Tests use `httpx.AsyncClient` with `ASGITransport` — no live server required.

---

## Frontend Test Execution

**Command** (foreground, from `web/`):
```powershell
cd web; npm run test
```

**Watch mode (interactive):**
```powershell
cd web; npm run test:watch
```

- Config: `web/vitest.config.ts`; setup in `web/src/test/setup.ts`

---

## Reporting Format

After execution, always report:

```
Test Suite: [Backend pytest | Frontend vitest]
─────────────────────────────────────────────
Total:    X tests
Passed:   X ✅
Failed:   X ❌
Skipped:  X ⏭️
Duration: X.XXs
```

For each **FAILURE**, report:
- Test name (full path)
- File and line number
- Error message (brief)
- Suggested fix (concrete — which file/function to change)

---

## Rules

- Never modify test files to make them pass — report the failure and suggest a source code fix.
- If tests fail due to missing dependencies: suggest the install command.
- If tests fail due to missing environment variables: point to `.env.example`.
- If tests fail due to missing DB: suggest running `alembic upgrade head` first.
- Run from repo root — use shell-native directory switching (`Set-Location` or `cd`).
