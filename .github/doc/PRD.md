# PRD: Todo AI — Phase-by-Phase Product Requirements

**Application**: Single-user Todo app with optional category support  
**Stack**: FastAPI (Python) · React 18 TypeScript · SQL Server  
**Author**: Product — Generated via `generate-prd` prompt  
**Date**: 2026-04-01

---

## Phase 0 — Foundation & Copilot Setup

### Problem Statement
No runnable application or developer tooling exists yet. Before any feature work
can begin, developers need a scaffolded monorepo, a working database connection,
and GitHub Copilot agent infrastructure in place so that every subsequent phase
can be driven by consistent AI-assisted workflows.

### User Stories
- **Given** I am a developer who has cloned the repo and created `.env` files,
  **When** I run `uvicorn app.main:app --reload` in `/api`,
  **Then** the server starts without errors and `GET /health` returns `200 {"status":"ok"}`.

- **Given** I am a developer,
  **When** I run `npm run dev` in `/web`,
  **Then** the Vite dev server starts without TypeScript errors and the app loads in the browser.

- **Given** I am a developer using Copilot Agent mode,
  **When** I type `@api` or `@web` in the chat,
  **Then** the corresponding agent is available and applies the correct instruction files automatically.

- **Given** I need to scaffold a new feature,
  **When** I open `.github/prompts/`,
  **Then** prompt files for PRD, TRD, DB migration, PR review, and commit message are all present.

- **Given** the `.env` file is missing,
  **When** I start the backend,
  **Then** the app logs a clear configuration error and exits — it does not start with defaults and silently fail.

### Acceptance Criteria
- [ ] `/api` and `/web` directories exist with all required dependency manifests (`requirements.txt`, `package.json`).
- [ ] `GET /health` returns HTTP 200 with `{"status": "ok"}` from the running backend.
- [ ] React dev server starts with zero TypeScript errors.
- [ ] Async SQL Server connection is established via `aioodbc` driver on startup.
- [ ] `api/.env.example` and `web/.env.example` are committed; no `.env` files are committed.
- [ ] Alembic is initialised and `alembic/env.py` uses the async migration runner pattern.
- [ ] `@api` agent and `@web` agent are defined in `.github/agents/` and load the correct instruction files.
- [ ] `generate-prd`, `generate-trd`, `pr-review`, `commit-message`, and `db-migration` prompt files exist in `.github/prompts/`.

### Edge Cases & Error States
- Missing `DATABASE_URL` in `.env` → startup raises a clear `pydantic_settings` validation error, process exits with non-zero code.
- `ODBC Driver 17 for SQL Server` not installed → connection error is logged clearly; no cryptic stack trace exposed to the user.
- Missing `VITE_API_BASE_URL` → Vite build/dev fails with a descriptive message from the env validation utility.

### Out of Scope
Authentication, CI/CD pipelines, containerisation (Docker), deployment to any cloud environment.

### Open Questions
None — foundation is fully specified by `copilot-instructions.md` and the instruction files.

---

## Phase 1 — Basic Todo CRUD (no category)

### Problem Statement
Users have no way to manage their tasks. The core value of the application is
creating, viewing, updating, and deleting todo items. This phase delivers the
minimum useful product.

### User Stories
- **Given** I am on the home page,
  **When** I fill in a title and submit the form,
  **Then** the new todo appears at the top of the list immediately without a page refresh.

- **Given** I have a list of todos,
  **When** I click the checkbox on a todo,
  **Then** its completion status toggles and the visual style updates to reflect the new state.

- **Given** I have a todo in the list,
  **When** I click the delete button,
  **Then** the todo is removed from the list immediately.

- **Given** I submit the create form with an empty title,
  **When** client-side validation runs,
  **Then** an error message appears and no HTTP request is sent.

- **Given** I request a todo by an ID that does not exist,
  **When** the API processes the request,
  **Then** a `404 Not Found` is returned with a human-readable `detail` message.

- **Given** I submit a title longer than 255 characters,
  **When** the API validates the payload,
  **Then** a `422 Unprocessable Entity` is returned with field-level validation details.

### Acceptance Criteria
- [ ] `POST /api/v1/todos` with valid payload → `201 Created` with `TodoResponse` JSON body.
- [ ] `GET /api/v1/todos` → `200 OK` with an array of todos ordered by `created_at` descending.
- [ ] `GET /api/v1/todos/{id}` with existing id → `200 OK`; with non-existent id → `404 Not Found`.
- [ ] `PUT /api/v1/todos/{id}` with partial or full update payload → `200 OK` with updated todo; non-existent id → `404`.
- [ ] `DELETE /api/v1/todos/{id}` → `204 No Content` on success; `404` if todo does not exist.
- [ ] `title` is required, minimum 1 character, maximum 255 characters.
- [ ] `description` is optional, maximum 1000 characters.
- [ ] `is_completed` defaults to `false` on creation.
- [ ] The frontend lists all todos, supports creating a new todo, toggling completion, and deleting.
- [ ] Every component using `useQuery` handles `isLoading`, `isError`, and empty state.
- [ ] Alembic migration `create_todos_table` is applied before testing.

### Edge Cases & Error States
- Empty string title → `422` from Pydantic `Field(min_length=1)`.
- Title exactly 256 characters → `422`.
- `description` exactly 1001 characters → `422`.
- Non-integer `{id}` in URL → FastAPI returns `422` automatically.
- `PUT` with an empty JSON body `{}` → `200` with unchanged todo (all fields optional in `TodoUpdate`).

### Out of Scope
Category assignment, filtering by status, pagination, full-text search, bulk operations.

### Open Questions
None.

---

## Phase 2 — Unit Tests (backend + frontend)

### Problem Statement
Phase 1 code is manually verified only. Without automated tests, regressions in
the core CRUD layer cannot be detected reliably as the codebase grows. This phase
locks in correctness for every public method before new complexity is added.

### User Stories
- **Given** all Phase 1 service methods are implemented,
  **When** `pytest -v` runs,
  **Then** every happy-path test passes with zero failures.

- **Given** the service calls `repository.get_by_id()` which returns `None`,
  **When** the test exercises this path,
  **Then** it asserts that an `HTTPException` with status `404` is raised.

- **Given** the `TodoList` component is rendered with `isLoading: true`,
  **When** the test queries the DOM,
  **Then** a loading indicator with role `"status"` is visible.

- **Given** the `TodoItem` component is rendered,
  **When** the user clicks the delete button,
  **Then** the `onDelete` handler is called exactly once with the correct todo `id`.

- **Given** the `TodoForm` is submitted with an empty title,
  **When** client-side validation runs,
  **Then** an error message is displayed and no mutation hook is called.

### Acceptance Criteria
- [ ] `pytest -v` passes with zero failures and zero errors.
- [ ] `vitest run` passes with zero failures.
- [ ] `TodoRepository` is tested for: `get_all` (empty, populated), `get_by_id` (found, not found), `create`, `update` (found, not found), `delete` (found, not found).
- [ ] `TodoService` is tested for: all CRUD paths; `404 HTTPException` raised where repository returns `None`; repository is mocked (not real DB).
- [ ] Route integration tests via `httpx.AsyncClient` cover all 5 endpoints including `422` for empty title and `404` for missing ID.
- [ ] Frontend component tests use `@testing-library/user-event` for interactions — not `.click()` directly.
- [ ] Service functions are mocked in frontend tests — React Query internals are never mocked directly.
- [ ] Test naming follows `test_<action>_<condition>_<expected_outcome>` convention.

### Edge Cases & Error States
- Service test: `get_by_id` with `None` return from mock → `HTTPException(status_code=404)` asserted.
- Service test: `create` → returned object has a populated `id` (flush gives the ID within the transaction).
- Route test: `DELETE` on non-existent id → body contains `"detail"` key with descriptive message.
- Frontend test: `isError` state → element with `role="alert"` is visible.
- Frontend test: empty todo list → "No todos yet" (or equivalent) message is rendered.

### Out of Scope
End-to-end (E2E) browser tests, code coverage percentage thresholds, performance/load tests, CI pipeline execution.

### Open Questions
None.

---

## Phase 3 — Add Category to Todo

### Problem Statement
All todos live in a flat, undifferentiated list. Users who manage tasks across
multiple projects or areas of responsibility have no way to group related work.
Categories provide a lightweight organisational layer without adding complexity.

### User Stories
- **Given** I am on the home page,
  **When** I create a new category with a unique name,
  **Then** it appears in the category list and is available in the todo form dropdown.

- **Given** I am creating a todo,
  **When** I select a category from the dropdown and submit,
  **Then** the todo is saved with that category and the category name appears as a badge next to the todo title.

- **Given** a todo has an assigned category,
  **When** I view the todo,
  **Then** the category name is rendered as a visible badge on the todo item.

- **Given** I try to create a category with a name that already exists (case-sensitive),
  **When** I submit,
  **Then** a `409 Conflict` error is returned and no duplicate is created.

- **Given** I delete a category,
  **When** I view todos that previously belonged to it,
  **Then** those todos display no category (the category badge is absent and `categoryId` is `null`).

- **Given** I create a todo with a `category_id` that does not exist,
  **When** the API processes the request,
  **Then** a `404 Not Found` is returned.

### Acceptance Criteria
- [ ] `POST /api/v1/categories` with valid `name` → `201 Created` with `CategoryResponse`.
- [ ] `GET /api/v1/categories` → `200 OK` with array of all categories.
- [ ] `GET /api/v1/categories/{id}` → `200` or `404`.
- [ ] `PUT /api/v1/categories/{id}` → `200` or `404`.
- [ ] `DELETE /api/v1/categories/{id}` → `204` or `404`; associated todos have `category_id` set to `null`.
- [ ] Category `name` is required, 1–100 characters, must be unique (case-sensitive).
- [ ] `TodoCreate` and `TodoUpdate` accept an optional `category_id` field.
- [ ] `TodoResponse` includes `category_id: int | null` and `category_name: str | null`.
- [ ] Alembic migration `create_categories_table` creates the `categories` table.
- [ ] Alembic migration `add_category_id_to_todos` adds nullable FK `category_id` to `todos`.
- [ ] Frontend `CategorySelect` dropdown is powered by live data from `useCategories` hook.
- [ ] Frontend `CategoryBadge` renders the category name or nothing when `categoryId` is `null`.

### Edge Cases & Error States
- Duplicate category name → `409 Conflict` with `"Category with name '...' already exists"`.
- `category_id` in todo payload referencing a non-existent category → `404 Not Found`.
- Deleting a category with assigned todos → todos' `category_id` becomes `null` (SQL `ON DELETE SET NULL`), todos are not deleted.
- Empty category name string → `422` from Pydantic `Field(min_length=1)`.
- Category name exactly 101 characters → `422`.

### Out of Scope
Category colours, icons, nested/hierarchical categories, assigning multiple categories per todo, filtering todos by category on the frontend.

### Open Questions
- **Resolved**: Deleting a category nullifies `category_id` on associated todos (`ON DELETE SET NULL`) — todos are NOT deleted.

---

## Phase 4 — Update & Expand Tests, Add Failing Edge Cases, Resolve Failures

### Problem Statement
Phase 3 introduced a new entity (Category), a foreign-key relationship, and
a duplicate-name constraint — all of which add new failure modes that are not
yet covered by tests. Any regressions introduced in Phase 3 must also be
identified and resolved here before the final review.

### User Stories
- **Given** all Category endpoints are implemented,
  **When** `pytest -v` runs,
  **Then** every Category CRUD path (happy + error) passes and no previously passing test regresses.

- **Given** a duplicate category name is submitted in a test,
  **When** the service call is executed,
  **Then** the test confirms a `409 HTTPException` is raised with the correct detail message.

- **Given** a category is deleted in a repository test,
  **When** the test fetches a todo that was previously assigned to it,
  **Then** the todo's `category_id` is `null`.

- **Given** `CategorySelect` is rendered with a mocked `useCategories` returning data,
  **When** the user selects an option,
  **Then** the `onChange` callback is called with the correct category `id`.

### Acceptance Criteria
- [ ] `pytest -v` → zero failures (all Phase 2 tests still pass + all new Category tests pass).
- [ ] `vitest run` → zero failures.
- [ ] `test_category_repository.py` covers: full CRUD, `get_by_name`, and FK nullification on delete.
- [ ] `test_category_service.py` covers: all CRUD + `409` on duplicate name + `404` on not found.
- [ ] `test_category_routes.py` covers: all 5 endpoints + `409` duplicate + `422` missing name.
- [ ] `test_todo_service.py` is updated with: `create with valid category_id succeeds`, `create with invalid category_id raises 404`, `update with category_id succeeds`.
- [ ] `test_todo_routes.py` is updated with: `create with category_id returns 201`, `create with invalid category_id returns 404`, `todo response includes category_name`.
- [ ] `CategoryBadge.test.tsx` covers: renders name, renders nothing when null.
- [ ] `CategorySelect.test.tsx` covers: loading state, renders options, selection fires onChange, placeholder shown when none selected.
- [ ] Any test failures from Phase 3 code are fixed in source — tests are never modified to force a pass.

### Edge Cases & Error States
- `CategoryService.create` with a name that exists → `409` with exact detail string tested.
- `TodoService.create` with `category_id` that does not exist → `404` tested.
- Category deleted → `todos.category_id = null` verified by repository test.
- Empty category list → `CategorySelect` shows a placeholder option.

### Out of Scope
Performance tests, load tests, mutation testing, code coverage badge/threshold enforcement.

### Open Questions
None.

---

## Phase 5 — Final Integration Run + Security Review

### Problem Statement
The application is feature-complete after Phase 4 but has not been reviewed
holistically for security vulnerabilities or end-to-end correctness. Before the
codebase is considered production-ready, a full test run and a structured
OWASP Top 10 security review must be completed and all findings resolved.

### User Stories
- **Given** all phases are complete,
  **When** the complete test suite runs (`pytest -v` + `vitest run`),
  **Then** every single test passes with zero failures and zero errors.

- **Given** the PR review prompt checklist is executed against all changed files,
  **When** each checklist item is evaluated,
  **Then** every item returns ✅ and no ❌ findings remain unresolved.

- **Given** a security review is performed against OWASP Top 10,
  **When** the codebase is analysed,
  **Then** no critical or high-severity vulnerabilities are present.

- **Given** a malicious payload containing SQL-injection characters is sent in the `title` field,
  **When** the API receives it,
  **Then** Pydantic validates the input and SQLAlchemy ORM parameterises the query — no SQL injection is possible.

- **Given** the frontend is audited for exposed secrets,
  **When** all source files are scanned,
  **Then** no hardcoded URLs, API keys, or credentials exist in any committed file.

### Acceptance Criteria
- [ ] `pytest -v` → 0 failures, 0 errors across all test files.
- [ ] `vitest run` → 0 failures across all test files.
- [ ] PR review prompt checklist returns all ✅ for: architecture compliance, type safety, security, async correctness, error handling, database, and test coverage sections.
- [ ] No hardcoded secrets, connection strings, or passwords in any source file.
- [ ] CORS is configured with an explicit origin allowlist from the environment — not a wildcard `"*"`.
- [ ] All user input is validated by Pydantic `Field` constraints before reaching the repository layer.
- [ ] No raw SQL string concatenation anywhere — SQLAlchemy ORM parameterised queries only.
- [ ] API error responses never expose internal stack traces or exception class names.
- [ ] No `.env` files are committed; `.env.example` files are present for both `/api` and `/web`.
- [ ] No `# type: ignore` or `@ts-ignore` without an explanatory justification comment.
- [ ] No `console.log()` left in TypeScript production code (except intentional debug with a comment).
- [ ] No commented-out code remains in any committed file.

### Edge Cases & Error States
- SQL injection attempt via `title` field → Pydantic `str` type + SQLAlchemy ORM completely neutralises it; `422` returned for characters that violate length constraints.
- XSS attempt via `title` field displayed in React → JSX auto-escaping prevents rendering; no `dangerouslySetInnerHTML` is used anywhere.
- Oversized payload (e.g., 10 MB body) → FastAPI's default body size limit or Pydantic field max-length returns `422`.
- `.env` file accidentally staged → pre-commit check (or PR review prompt) catches it before merge.

### Out of Scope
Authentication and authorisation (OAuth, JWT), rate limiting, HTTPS termination, WAF configuration, deployment hardening, penetration testing, SAST/DAST tooling integration.

### Open Questions
None — all security decisions are specified in `copilot-instructions.md` and the `pr-review` prompt.
