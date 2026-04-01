# TRD: Todo AI — Phase-by-Phase Technical Requirements

**Application**: Single-user Todo app with optional category support  
**Stack**: FastAPI · SQLAlchemy 2.x async · SQL Server · React 18 TypeScript · Vite  
**Author**: Architecture — Generated via `generate-trd` prompt  
**Date**: 2026-04-01

> **Reading guide**: Each phase builds on the previous. Only net-new files and
> changes are listed per phase. Implement phases strictly in order.

---

## Phase 0 — Foundation & Copilot Setup

### Feature Summary
Bootstrap the monorepo: FastAPI skeleton connected to SQL Server via async
`aioodbc`, Vite + React + TypeScript frontend, Alembic initialised for async
migrations, and all Copilot agent/prompt/instruction files in place.

### Database Changes
No application tables. Alembic creates only the `alembic_version` tracking table.

```
alembic upgrade head   # creates alembic_version only
```

Connection string pattern (from `.env`):
```
DATABASE_URL=mssql+aioodbc://sa:<password>@localhost:1433/todo_db?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes
```

### API Contract

| Method | Path      | Request Body | Response                  | Status Codes |
|--------|-----------|--------------|---------------------------|--------------|
| GET    | /health   | —            | `{"status": "ok"}`        | 200          |

### Backend Implementation

**Files to create (strictly in this order)**:

| # | Path | Purpose |
|---|------|---------|
| 1 | `api/requirements.txt` | `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]`, `aioodbc`, `alembic`, `pydantic-settings`, `python-dotenv`, `pyodbc`, `pytest`, `pytest-asyncio`, `httpx` |
| 2 | `api/.env.example` | `DATABASE_URL`, `APP_ENV=development`, `ALLOWED_ORIGINS=http://localhost:5173` |
| 3 | `api/app/__init__.py` | Empty |
| 4 | `api/app/config.py` | `pydantic-settings` `Settings` class; loads `DATABASE_URL`, `APP_ENV`, `ALLOWED_ORIGINS` from `.env`; raises on missing required vars |
| 5 | `api/app/db/__init__.py` | Empty |
| 6 | `api/app/db/base.py` | `DeclarativeBase` — `class Base(DeclarativeBase): pass` |
| 7 | `api/app/db/session.py` | `create_async_engine`, `async_sessionmaker`, `get_db()` async generator; engine URL from `Settings` |
| 8 | `api/app/main.py` | `FastAPI` app factory; `CORSMiddleware` with `allow_origins` from `Settings.ALLOWED_ORIGINS` (never `"*"`); `GET /health` route; no routers yet |
| 9 | `api/alembic.ini` | `sqlalchemy.url` left as placeholder — overridden in `env.py` from `Settings` |
| 10 | `api/alembic/env.py` | Async migration runner using `run_async_migrations` pattern; imports `Base` from `app.db.base`; reads URL from `Settings` |

**Alembic async `env.py` pattern**:
```python
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from alembic import context
from app.db.base import Base
from app.config import Settings

settings = Settings()

def run_migrations_online() -> None:
    configuration = context.config.get_section(context.config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = async_engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)

    async def run_async_migrations() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()

    asyncio.run(run_async_migrations())

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
```

### Error Handling Strategy

| Scenario | Behaviour |
|----------|-----------|
| Missing `DATABASE_URL` in env | `pydantic_settings` `ValidationError` on startup; process exits with non-zero code |
| DB connection failure at startup | `aioodbc` raises; logged at `ERROR` level; process exits |

### Frontend Implementation

**Files to create (strictly in this order)**:

| # | Path | Purpose |
|---|------|---------|
| 1 | `web/package.json` | `react`, `react-dom`, `@tanstack/react-query`, `axios`; dev: `vite`, `typescript`, `vitest`, `@testing-library/react`, `@testing-library/user-event`, `jsdom`, `zod` |
| 2 | `web/tsconfig.json` | `strict: true`, `paths: { "@/*": ["./src/*"] }` |
| 3 | `web/vite.config.ts` | Plugin `react()`, `test: { environment: "jsdom" }` |
| 4 | `web/.env.example` | `VITE_API_BASE_URL=http://localhost:8000/api/v1` |
| 5 | `web/src/services/api.ts` | Axios instance; `baseURL: import.meta.env.VITE_API_BASE_URL` |
| 6 | `web/src/types/index.ts` | Empty barrel file (populated in Phase 1) |
| 7 | `web/src/App.tsx` | `QueryClientProvider` wrapping placeholder `<main>` |
| 8 | `web/src/main.tsx` | `ReactDOM.createRoot` entry point |

### Copilot Agent Mode Prompts

```
1. @api Create the /api directory scaffold as specified in copilot-instructions.md.
   Create: requirements.txt, .env.example, app/__init__.py, app/config.py (pydantic-settings
   Settings loading DATABASE_URL / APP_ENV / ALLOWED_ORIGINS), app/db/base.py (DeclarativeBase),
   app/db/session.py (create_async_engine + async_sessionmaker + get_db async generator),
   app/main.py (FastAPI app, CORSMiddleware with origins from Settings, GET /health returning
   {"status":"ok"}).

2. @api Initialise Alembic in /api. Write alembic.ini with placeholder sqlalchemy.url.
   Write alembic/env.py using the run_async_migrations pattern for SQL Server via aioodbc.
   Import Base from app.db.base. Read DATABASE_URL from app.config.Settings.

3. @web Create the /web Vite React TypeScript project. Install @tanstack/react-query@5, axios,
   vitest, @testing-library/react, @testing-library/user-event, jsdom, zod.
   Configure tsconfig.json with strict mode and @/* path alias.
   Create src/services/api.ts (Axios instance with VITE_API_BASE_URL).
   Create src/types/index.ts empty barrel.
   Create src/App.tsx with QueryClientProvider.
   Create .env.example with VITE_API_BASE_URL.
```

### Testing Plan
Manual verification only:
- `uvicorn app.main:app --reload` → starts, `GET /health` → `200 {"status":"ok"}`.
- `npm run dev` → starts, browser renders app without console errors.
- `alembic upgrade head` → succeeds, `alembic_version` table exists in DB.

### Breaking Changes
None — greenfield.

---

## Phase 1 — Basic Todo CRUD (no category)

### Feature Summary
Implement full Todo CRUD across all three backend layers (Model → Schema →
Repository → Service → Routes) and the full frontend stack (Types → Service →
Hooks → Components → Page). No category support yet.

### Database Changes
**New table: `todos`**

| Column | SQL Server Type | Constraints |
|--------|----------------|-------------|
| `id` | `INT IDENTITY(1,1)` | `PRIMARY KEY` |
| `title` | `NVARCHAR(255)` | `NOT NULL` |
| `description` | `NVARCHAR(1000)` | `NULL` |
| `is_completed` | `BIT` | `NOT NULL DEFAULT 0` |
| `created_at` | `DATETIME` | `NOT NULL DEFAULT GETDATE()` |
| `updated_at` | `DATETIME` | `NOT NULL DEFAULT GETDATE()` |

```bash
cd api
alembic revision --autogenerate -m "create_todos_table"
# Review generated file: verify NVARCHAR types, not VARCHAR
alembic upgrade head
```

### API Contract

| Method | Path | Request Body | Response | Status Codes |
|--------|------|--------------|----------|--------------|
| POST | `/api/v1/todos` | `TodoCreate` | `TodoResponse` | 201, 422 |
| GET | `/api/v1/todos` | — | `list[TodoResponse]` | 200 |
| GET | `/api/v1/todos/{id}` | — | `TodoResponse` | 200, 404 |
| PUT | `/api/v1/todos/{id}` | `TodoUpdate` | `TodoResponse` | 200, 404, 422 |
| DELETE | `/api/v1/todos/{id}` | — | — | 204, 404 |

**Schema definitions**:
```python
# TodoCreate
{ "title": "string (1–255, required)", "description": "string (max 1000, optional)" }

# TodoUpdate  (all optional)
{ "title": "string (1–255)", "description": "string (max 1000)", "is_completed": "bool" }

# TodoResponse
{
  "id": int, "title": str, "description": str | None,
  "is_completed": bool, "created_at": datetime, "updated_at": datetime
}
```

### Backend Implementation

**Files to create (strictly in this order)**:

| # | Path | Purpose |
|---|------|---------|
| 1 | `api/app/models/__init__.py` | `from app.models.todo import Todo` |
| 2 | `api/app/models/todo.py` | `Todo` ORM model — `Mapped` / `mapped_column`; all fields shown in DB Changes |
| 3 | `api/app/schemas/__init__.py` | Empty |
| 4 | `api/app/schemas/todo.py` | `TodoCreate`, `TodoUpdate`, `TodoResponse` (Pydantic v2, `ConfigDict(from_attributes=True)`) |
| 5 | `api/app/repositories/__init__.py` | Empty |
| 6 | `api/app/repositories/todo_repository.py` | `TodoRepository` — `get_all`, `get_by_id`, `create`, `update`, `delete` |
| 7 | `api/app/services/__init__.py` | Empty |
| 8 | `api/app/services/todo_service.py` | `TodoService` — orchestrates repo calls, raises `HTTPException`, commits |
| 9 | `api/app/routes/__init__.py` | Empty |
| 10 | `api/app/routes/todo_router.py` | `APIRouter(prefix="/api/v1/todos", tags=["todos"])` — all 5 endpoints |
| 11 | `api/app/main.py` *(update)* | `app.include_router(todo_router)` |
| 12 | `api/alembic/versions/<hash>_create_todos_table.py` | Generated by Alembic; reviewed for correctness |

**`Todo` model**:
```python
class Todo(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
```

**`TodoRepository` method signatures**:
```python
async def get_all(self) -> list[Todo]                          # ORDER BY created_at DESC
async def get_by_id(self, todo_id: int) -> Todo | None
async def create(self, data: TodoCreate) -> Todo               # flush (no commit)
async def update(self, todo_id: int, data: TodoUpdate) -> Todo | None
async def delete(self, todo_id: int) -> bool                   # True if deleted, False if not found
```

**`TodoService` method signatures**:
```python
async def get_all(self) -> list[Todo]
async def get_by_id(self, todo_id: int) -> Todo                # raises 404 if None
async def create(self, data: TodoCreate) -> Todo               # commits after flush
async def update(self, todo_id: int, data: TodoUpdate) -> Todo # raises 404 if not found
async def delete(self, todo_id: int) -> None                   # raises 404 if not found
```

**Route DI chain**:
```python
# session.py
async def get_db() -> AsyncGenerator[AsyncSession, None]: ...

# todo_repository.py
async def get_todo_repository(session: Annotated[AsyncSession, Depends(get_db)]) -> TodoRepository:
    return TodoRepository(session)

# todo_service.py
async def get_todo_service(repo: Annotated[TodoRepository, Depends(get_todo_repository)]) -> TodoService:
    return TodoService(repo)

# todo_router.py
@router.post("/", response_model=TodoResponse, status_code=201)
async def create_todo(payload: TodoCreate, service: Annotated[TodoService, Depends(get_todo_service)]) -> TodoResponse:
    return await service.create(payload)
```

### Error Handling Strategy

| Scenario | HTTP Code | Error `detail` Message |
|----------|-----------|------------------------|
| Todo not found (get/update/delete) | 404 | `"Todo with id {id} not found"` |
| `title` is empty string | 422 | Pydantic field validation error (auto) |
| `title` > 255 chars | 422 | Pydantic field validation error (auto) |
| `description` > 1000 chars | 422 | Pydantic field validation error (auto) |
| Non-integer `{id}` in path | 422 | FastAPI path parameter validation (auto) |

### Frontend Implementation

**Files to create (strictly in this order)**:

| # | Path | Purpose |
|---|------|---------|
| 1 | `web/src/types/todo.ts` | `Todo`, `TodoCreate`, `TodoUpdate` interfaces |
| 2 | `web/src/types/index.ts` *(update)* | `export * from './todo'` |
| 3 | `web/src/services/todoService.ts` | `getAll`, `getById`, `create`, `update`, `delete` — all via `api` Axios instance |
| 4 | `web/src/hooks/useTodos.ts` | `useTodos`, `useCreateTodo`, `useUpdateTodo`, `useDeleteTodo` — React Query v5 |
| 5 | `web/src/components/TodoItem.tsx` | Props: `todo: Todo`; renders title, description, checkbox toggle, delete button; shows strikethrough when completed |
| 6 | `web/src/components/TodoList.tsx` | Uses `useTodos`; handles `isLoading` (`role="status"`), `isError` (`role="alert"`), empty state, populated list |
| 7 | `web/src/components/TodoForm.tsx` | Controlled form; `title` required; calls `useCreateTodo`; clears on success |
| 8 | `web/src/pages/HomePage.tsx` | Composes `<TodoForm />` + `<TodoList />` |
| 9 | `web/src/App.tsx` *(update)* | Render `<HomePage />` inside `QueryClientProvider` |

**`Todo` TypeScript interface**:
```typescript
// src/types/todo.ts
export interface Todo {
  id: number;
  title: string;
  description: string | null;
  isCompleted: boolean;
  createdAt: string;
  updatedAt: string;
}
export interface TodoCreate { title: string; description?: string; }
export interface TodoUpdate { title?: string; description?: string; isCompleted?: boolean; }
```

> **Note**: FastAPI returns `snake_case` fields. Configure Axios response
> interceptor or FastAPI `alias_generator` to map `is_completed → isCompleted`.
> Preferred approach: add `model_config = ConfigDict(populate_by_name=True)` and
> use `alias_generator=to_camel` from `pydantic.alias_generators` in `TodoResponse`.

**Hook invalidation keys**:
```typescript
queryKey: ['todos']            // useTodos
queryKey: ['todos', id]        // useTodo(id)
// mutations invalidate: { queryKey: ['todos'] }
```

### Copilot Agent Mode Prompts

```
1. @api Create api/app/models/todo.py with a Todo SQLAlchemy 2.x ORM model using
   Mapped/mapped_column. Fields: id (PK, index), title (NVARCHAR 255, not null),
   description (NVARCHAR 1000, nullable), is_completed (bool, default False, not null),
   created_at / updated_at (DateTime, server_default func.now(), updated_at has onupdate).
   Export from models/__init__.py.

2. @api Create api/app/schemas/todo.py with Pydantic v2 schemas.
   TodoCreate: title (str, min_length=1, max_length=255), description (str|None, max_length=1000).
   TodoUpdate: all fields Optional. TodoResponse: id, is_completed, created_at, updated_at,
   ConfigDict(from_attributes=True). Use alias_generator=to_camel for camelCase JSON output.

3. @api Create api/app/repositories/todo_repository.py with TodoRepository class.
   Async methods: get_all (select ordered by created_at desc), get_by_id (returns Todo|None),
   create (flush not commit), update (execute update statement return updated Todo|None),
   delete (returns bool). Use SQLAlchemy 2.x select/update/delete statements only.

4. @api Create api/app/services/todo_service.py with TodoService class.
   All methods async. get_by_id raises HTTPException 404 when repo returns None.
   create: calls repo.create, then session.commit(), then session.refresh(todo).
   update: raises 404 if not found, commits on success.
   delete: raises 404 if not found, commits on success. Log all operations.

5. @api Create api/app/routes/todo_router.py with APIRouter(prefix="/api/v1/todos",
   tags=["todos"]). Five endpoints: POST / (201), GET / (200), GET /{id} (200/404),
   PUT /{id} (200/404), DELETE /{id} (204/404). Use Annotated[TodoService, Depends(get_todo_service)]
   for all routes. Register router in app/main.py.

6. @api Run: cd api && alembic revision --autogenerate -m "create_todos_table"
   Review the generated migration — verify NVARCHAR types and NOT NULL constraints.
   Then run: alembic upgrade head

7. @web Create web/src/types/todo.ts (Todo, TodoCreate, TodoUpdate interfaces with camelCase fields).
   Create web/src/services/todoService.ts (getAll, getById, create, update, delete via api.ts).
   Create web/src/hooks/useTodos.ts (useTodos, useCreateTodo, useUpdateTodo, useDeleteTodo with
   React Query v5 invalidating ['todos'] on all mutations).

8. @web Create TodoItem.tsx (displays title, description, checkbox for is_completed, delete button),
   TodoList.tsx (uses useTodos, handles isLoading with role=status, isError with role=alert,
   empty state, and populated list), TodoForm.tsx (controlled form, title required, uses
   useCreateTodo, clears on success). Compose in src/pages/HomePage.tsx.
```

### Testing Plan
Manual smoke testing only in Phase 1. Phase 2 adds automated tests.

Verify manually:
- `POST /api/v1/todos` with `{"title":"Test"}` → `201`, response includes `id`.
- `GET /api/v1/todos` → `200` array.
- `GET /api/v1/todos/999` → `404`.
- Frontend: create todo → appears in list. Toggle → style changes. Delete → removed.

### Breaking Changes
None — Phase 0 had no application endpoints.

---

## Phase 2 — Unit Tests (backend + frontend)

### Feature Summary
Write automated tests for all Phase 1 backend and frontend code. No new
application features — tests only.

### Database Changes
None.

### API Contract
No new endpoints.

### Backend Implementation

**Files to create**:

| # | Path | Purpose |
|---|------|---------|
| 1 | `api/tests/__init__.py` | Empty |
| 2 | `api/tests/conftest.py` | Shared fixtures: in-memory async session (SQLite for repo tests), `httpx.AsyncClient` for route tests, mock service/repo fixtures |
| 3 | `api/tests/test_todo_repository.py` | Repository tests with real async SQLite session |
| 4 | `api/tests/test_todo_service.py` | Service tests with mocked `AsyncMock` repository |
| 5 | `api/tests/test_todo_routes.py` | Route integration tests via `httpx.AsyncClient` |

**`conftest.py` key fixtures**:
```python
@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    # SQLite in-memory with async engine for repository tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        yield session

@pytest.fixture
async def client(async_session) -> AsyncGenerator[AsyncClient, None]:
    # Override get_db dependency, yield httpx.AsyncClient
    app.dependency_overrides[get_db] = lambda: async_session
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
```

**`test_todo_repository.py` — test cases**:

| Test Name | Assertion |
|-----------|-----------|
| `test_get_all_returns_empty_list` | Returns `[]` when no todos exist |
| `test_get_all_returns_all_todos` | Returns all seeded todos ordered by `created_at` desc |
| `test_get_by_id_returns_todo` | Returns correct `Todo` object |
| `test_get_by_id_returns_none_when_not_found` | Returns `None` for unknown id |
| `test_create_returns_todo_with_id` | Created todo has `id` populated after flush |
| `test_update_returns_updated_todo` | `title` reflects new value |
| `test_update_returns_none_when_not_found` | Returns `None` for unknown id |
| `test_delete_returns_true_on_success` | Returns `True` and todo no longer retrievable |
| `test_delete_returns_false_when_not_found` | Returns `False` for unknown id |

**`test_todo_service.py` — test cases**:

| Test Name | Assertion |
|-----------|-----------|
| `test_get_all_returns_list` | Delegates to repo, returns its result |
| `test_get_by_id_returns_todo` | Returns todo when repo returns one |
| `test_get_by_id_raises_404_when_not_found` | `HTTPException` status 404 when repo returns `None` |
| `test_create_returns_new_todo` | Calls repo.create, commits, refreshes, returns todo |
| `test_update_returns_updated_todo` | Calls repo.update, commits, returns todo |
| `test_update_raises_404_when_not_found` | `HTTPException` 404 when repo returns `None` |
| `test_delete_success` | Calls repo.delete, commits |
| `test_delete_raises_404_when_not_found` | `HTTPException` 404 when repo returns `False` |

**`test_todo_routes.py` — test cases**:

| Test Name | Expected Status |
|-----------|----------------|
| `test_create_todo_returns_201` | `201` + `id` in response body |
| `test_create_todo_returns_422_on_missing_title` | `422` |
| `test_create_todo_returns_422_on_empty_title` | `422` |
| `test_list_todos_returns_200` | `200` + array |
| `test_get_todo_returns_200` | `200` |
| `test_get_todo_returns_404` | `404` + `"detail"` key |
| `test_update_todo_returns_200` | `200` + updated field |
| `test_update_todo_returns_404` | `404` |
| `test_delete_todo_returns_204` | `204` + empty body |
| `test_delete_todo_returns_404` | `404` |

### Error Handling Strategy
Tests assert exact HTTP status codes and verify `"detail"` key exists in error response bodies. Service tests use `pytest.raises(HTTPException)` and check `exc_info.value.status_code`.

### Frontend Implementation

**Files to create**:

| # | Path | Purpose |
|---|------|---------|
| 1 | `web/src/components/TodoItem.test.tsx` | RTL tests for `TodoItem` |
| 2 | `web/src/components/TodoList.test.tsx` | RTL tests for `TodoList` |
| 3 | `web/src/components/TodoForm.test.tsx` | RTL tests for `TodoForm` |

**`TodoItem.test.tsx` — test cases**:

| Test Name | Assertion |
|-----------|-----------|
| `test renders todo title` | Title text is visible |
| `test renders description when provided` | Description text is visible |
| `test calls onToggle when checkbox is clicked` | `onToggle` called with todo `id` |
| `test calls onDelete when delete button is clicked` | `onDelete` called with todo `id` |
| `test shows completed style when isCompleted is true` | Completed class/style applied |

**`TodoList.test.tsx` — test cases**:

| Test Name | Assertion |
|-----------|-----------|
| `test shows loading indicator while fetching` | `role="status"` element visible |
| `test shows error message on fetch error` | `role="alert"` element visible |
| `test shows empty state when no todos` | "No todos" (or equivalent) text visible |
| `test renders list of todos` | Each todo title is visible |

**`TodoForm.test.tsx` — test cases**:

| Test Name | Assertion |
|-----------|-----------|
| `test submits with valid title` | Mutation hook called with title payload |
| `test shows validation error when title is empty` | Error message rendered, mutation not called |
| `test clears form after successful submission` | Input value is empty after submit |

**Mocking pattern**:
```typescript
vi.mock('@/hooks/useTodos', () => ({
  useTodos: vi.fn(),
  useCreateTodo: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useDeleteTodo: vi.fn(() => ({ mutate: vi.fn() })),
}));
```

### Copilot Agent Mode Prompts

```
1. @api Create api/tests/conftest.py. Fixture async_session: SQLite in-memory async engine,
   creates all tables from Base.metadata, yields AsyncSession. Fixture client: overrides
   get_db with async_session, yields httpx.AsyncClient pointed at the FastAPI app.
   Use pytest.ini_options asyncio_mode = "auto".

2. @api Create api/tests/test_todo_repository.py. Use async_session fixture.
   Test all TodoRepository methods: get_all (empty + seeded), get_by_id (found + None),
   create (id populated), update (found + not found), delete (True + False). pytest-asyncio.

3. @api Create api/tests/test_todo_service.py. Mock TodoRepository with unittest.mock.AsyncMock.
   Test all TodoService methods. For not-found cases assert pytest.raises(HTTPException)
   with status_code 404. Test that commit and refresh are called after create.

4. @api Create api/tests/test_todo_routes.py using the client fixture.
   Test all 5 CRUD endpoints. Include 422 for empty title, 404 for unknown id,
   204 with empty body for delete. Assert "detail" key in 404 responses.

5. @web Create TodoItem.test.tsx, TodoList.test.tsx, TodoForm.test.tsx using Vitest and RTL.
   Mock hooks via vi.mock('@/hooks/useTodos'). Use userEvent for interactions.
   TodoList tests: set mock return values for isLoading, isError, data states.
   TodoForm tests: assert mutation is called or not called based on input validity.
   Run vitest run to verify all pass.
```

### Testing Plan
- `cd api && pytest -v` → all 27 tests pass (9 repo + 8 service + 10 route).
- `cd web && vitest run` → all 13 tests pass (5 TodoItem + 4 TodoList + 4 TodoForm).

### Breaking Changes
None.

---

## Phase 3 — Add Category to Todo

### Feature Summary
Introduce `Category` as a first-class entity with full CRUD. Add a nullable
`category_id` FK on `todos`. Update `TodoResponse` to include `category_name`.
Add frontend `CategoryBadge` and `CategorySelect` components.

### Database Changes

**New table: `categories`**

| Column | SQL Server Type | Constraints |
|--------|----------------|-------------|
| `id` | `INT IDENTITY(1,1)` | `PRIMARY KEY` |
| `name` | `NVARCHAR(100)` | `NOT NULL UNIQUE` |
| `created_at` | `DATETIME` | `NOT NULL DEFAULT GETDATE()` |
| `updated_at` | `DATETIME` | `NOT NULL DEFAULT GETDATE()` |

**Modified table: `todos`**

| Column | SQL Server Type | Constraints |
|--------|----------------|-------------|
| `category_id` | `INT` | `NULL`, `FK → categories(id) ON DELETE SET NULL` |

**Migration sequence** (two separate migrations, applied in order):

```bash
# Migration 1
alembic revision --autogenerate -m "create_categories_table"
# Review: verify NVARCHAR, UNIQUE constraint, no accidental drops
alembic upgrade head

# Migration 2
alembic revision --autogenerate -m "add_category_id_to_todos"
# Review: verify nullable FK, ON DELETE SET NULL, correct downgrade drops FK before table
alembic upgrade head
```

> **Safety**: `category_id` is added as `NULL` — no backfill required.
> `downgrade()` must drop the FK constraint before dropping `categories` table.

### API Contract

**New Category endpoints**:

| Method | Path | Request Body | Response | Status Codes |
|--------|------|--------------|----------|--------------|
| POST | `/api/v1/categories` | `CategoryCreate` | `CategoryResponse` | 201, 422 |
| GET | `/api/v1/categories` | — | `list[CategoryResponse]` | 200 |
| GET | `/api/v1/categories/{id}` | — | `CategoryResponse` | 200, 404 |
| PUT | `/api/v1/categories/{id}` | `CategoryUpdate` | `CategoryResponse` | 200, 404, 422 |
| DELETE | `/api/v1/categories/{id}` | — | — | 204, 404 |

**Updated Todo endpoints** (modified schemas only):

| Method | Path | Change |
|--------|------|--------|
| POST | `/api/v1/todos` | `TodoCreate` gains optional `categoryId`; `TodoResponse` gains `categoryId`, `categoryName` |
| PUT | `/api/v1/todos/{id}` | `TodoUpdate` gains optional `categoryId`; `TodoResponse` gains `categoryId`, `categoryName` |
| GET | `/api/v1/todos` / `/{id}` | `TodoResponse` gains `categoryId`, `categoryName` |

**Schema definitions**:
```python
# CategoryCreate
{ "name": "string (1–100, required)" }

# CategoryUpdate (all optional)
{ "name": "string (1–100)" }

# CategoryResponse
{ "id": int, "name": str, "createdAt": datetime, "updatedAt": datetime }

# TodoResponse (updated)
{
  "id": int, "title": str, "description": str | None, "isCompleted": bool,
  "categoryId": int | None, "categoryName": str | None,
  "createdAt": datetime, "updatedAt": datetime
}
```

### Backend Implementation

**Files to create (strictly in this order)**:

| # | Path | Purpose |
|---|------|---------|
| 1 | `api/app/models/category.py` | `Category` ORM model |
| 2 | `api/app/models/__init__.py` *(update)* | `from app.models.category import Category` |
| 3 | `api/app/models/todo.py` *(update)* | Add `category_id` FK column + `category` relationship |
| 4 | `api/app/schemas/category.py` | `CategoryCreate`, `CategoryUpdate`, `CategoryResponse` |
| 5 | `api/app/schemas/todo.py` *(update)* | Add `category_id: int | None` to Create/Update; add `category_name: str | None` to Response |
| 6 | `api/app/repositories/category_repository.py` | `CategoryRepository` — `get_all`, `get_by_id`, `get_by_name`, `create`, `update`, `delete` |
| 7 | `api/app/repositories/todo_repository.py` *(update)* | Add `options(selectinload(Todo.category))` to `get_all` and `get_by_id` |
| 8 | `api/app/services/category_service.py` | `CategoryService` — CRUD + 409 on duplicate + 404 on not found |
| 9 | `api/app/services/todo_service.py` *(update)* | Validate `category_id` via `category_repo.get_by_id()` before create/update |
| 10 | `api/app/routes/category_router.py` | `APIRouter(prefix="/api/v1/categories", tags=["categories"])` |
| 11 | `api/app/main.py` *(update)* | `app.include_router(category_router)` |
| 12 | Two Alembic migration files | As described in Database Changes |

**`Category` model**:
```python
class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    todos: Mapped[list["Todo"]] = relationship("Todo", back_populates="category")
```

**`Todo` model updates**:
```python
# Add to Todo class:
category_id: Mapped[int | None] = mapped_column(
    Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
)
category: Mapped["Category | None"] = relationship("Category", back_populates="todos")
```

**`TodoResponse` update** (populate `category_name` from relationship):
```python
class TodoResponse(TodoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_completed: bool
    category_id: int | None
    category_name: str | None = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def populate_category_name(self) -> "TodoResponse":
        # Populated by service layer or via ORM relationship
        return self
```
> Preferred: set `category_name` from `todo.category.name if todo.category else None` in the service before returning. Do not put business logic in Pydantic validators.

**`CategoryRepository` method signatures**:
```python
async def get_all(self) -> list[Category]
async def get_by_id(self, category_id: int) -> Category | None
async def get_by_name(self, name: str) -> Category | None
async def create(self, data: CategoryCreate) -> Category      # flush, no commit
async def update(self, category_id: int, data: CategoryUpdate) -> Category | None
async def delete(self, category_id: int) -> bool
```

**`CategoryService` logic**:
- `create`: call `get_by_name`; if result → raise `HTTPException(409, "Category with name '{name}' already exists")`.
- `get_by_id` / `update` / `delete`: raise `HTTPException(404, "Category with id {id} not found")` when repo returns `None`/`False`.

**`TodoService` update logic**:
- `create` / `update`: if `data.category_id` is not `None`, call `category_repo.get_by_id(data.category_id)`; if `None` → raise `HTTPException(404, "Category with id {id} not found")`.
- `TodoService.__init__` must accept a second parameter: `category_repository: CategoryRepository`.

### Error Handling Strategy

| Scenario | HTTP Code | Error `detail` Message |
|----------|-----------|------------------------|
| Category not found | 404 | `"Category with id {id} not found"` |
| Duplicate category name | 409 | `"Category with name '{name}' already exists"` |
| Todo not found | 404 | `"Todo with id {id} not found"` |
| `category_id` in todo references non-existent category | 404 | `"Category with id {id} not found"` |
| `name` empty string | 422 | Pydantic field validation (auto) |
| `name` > 100 chars | 422 | Pydantic field validation (auto) |

### Frontend Implementation

**Files to create (strictly in this order)**:

| # | Path | Purpose |
|---|------|---------|
| 1 | `web/src/types/category.ts` | `Category`, `CategoryCreate`, `CategoryUpdate` interfaces |
| 2 | `web/src/types/todo.ts` *(update)* | Add `categoryId: number \| null`, `categoryName: string \| null` to `Todo` |
| 3 | `web/src/types/index.ts` *(update)* | `export * from './category'` |
| 4 | `web/src/services/categoryService.ts` | `getAll`, `getById`, `create`, `update`, `delete` via `api.ts` |
| 5 | `web/src/hooks/useCategories.ts` | `useCategories`, `useCreateCategory`, `useUpdateCategory`, `useDeleteCategory` |
| 6 | `web/src/components/CategoryBadge.tsx` | Props: `categoryName: string \| null`; renders chip or `null` |
| 7 | `web/src/components/CategorySelect.tsx` | Props: `value: number \| null`, `onChange: (id: number \| null) => void`; uses `useCategories` |
| 8 | `web/src/components/TodoItem.tsx` *(update)* | Render `<CategoryBadge categoryName={todo.categoryName} />` |
| 9 | `web/src/components/TodoForm.tsx` *(update)* | Add `<CategorySelect />` field; include `categoryId` in mutation payload |

**`Category` TypeScript interface**:
```typescript
// src/types/category.ts
export interface Category { id: number; name: string; createdAt: string; updatedAt: string; }
export interface CategoryCreate { name: string; }
export interface CategoryUpdate { name?: string; }
```

**Query keys**:
```typescript
queryKey: ['categories']        // useCategories
queryKey: ['categories', id]    // useCategory(id)
// mutations invalidate: { queryKey: ['categories'] }
```

### Copilot Agent Mode Prompts

```
1. @api Create api/app/models/category.py with Category SQLAlchemy 2.x ORM model.
   Fields: id (PK), name (NVARCHAR 100, UNIQUE, not null), created_at, updated_at.
   Add relationship todos back-populates category. Export from models/__init__.py.

2. @api Update api/app/models/todo.py: add category_id (Integer, nullable FK to
   categories.id ON DELETE SET NULL, indexed) and category relationship
   (back_populates="todos"). Import ForeignKey, Integer from sqlalchemy.

3. @api Create api/app/schemas/category.py: CategoryCreate (name str 1-100),
   CategoryUpdate (name optional), CategoryResponse (id, name, createdAt, updatedAt,
   from_attributes=True, alias_generator=to_camel). Update api/app/schemas/todo.py:
   add category_id (int|None) to TodoCreate and TodoUpdate, add category_name (str|None)
   to TodoResponse.

4. @api Create api/app/repositories/category_repository.py with CategoryRepository.
   Methods: get_all, get_by_id, get_by_name, create (flush), update, delete (bool).
   Update TodoRepository.get_all and get_by_id to eager-load category with
   options(selectinload(Todo.category)).

5. @api Create api/app/services/category_service.py. On create: call get_by_name;
   raise HTTPException 409 if name exists. On get/update/delete: raise 404 if not found.
   Update TodoService to accept CategoryRepository in __init__. On todo create/update:
   if category_id is not None, validate it exists via category_repo.get_by_id;
   raise 404 if not. Update get_todo_service DI function accordingly.

6. @api Create api/app/routes/category_router.py with APIRouter prefix /api/v1/categories.
   All 5 CRUD endpoints. Register in app/main.py.

7. @api Run: alembic revision --autogenerate -m "create_categories_table" && alembic upgrade head
   Review migration: NVARCHAR type, UNIQUE constraint, correct downgrade.
   Then: alembic revision --autogenerate -m "add_category_id_to_todos" && alembic upgrade head
   Review migration: nullable FK, ON DELETE SET NULL, downgrade drops FK before table.

8. @web Create web/src/types/category.ts, web/src/services/categoryService.ts,
   web/src/hooks/useCategories.ts following the same patterns as the todo domain.
   Update src/types/todo.ts to add categoryId and categoryName fields.

9. @web Create CategoryBadge.tsx (returns null when categoryName is null, otherwise renders
   a styled chip). Create CategorySelect.tsx (uses useCategories to render <select> with
   a "No category" option; calls onChange with id or null).
   Update TodoItem.tsx to render <CategoryBadge categoryName={todo.categoryName} />.
   Update TodoForm.tsx to include <CategorySelect /> and pass categoryId in create payload.
```

### Testing Plan
Manual smoke testing in Phase 3. Phase 4 adds automated Category tests.

Verify manually:
- `POST /api/v1/categories {"name":"Work"}` → `201`.
- `POST /api/v1/categories {"name":"Work"}` again → `409`.
- `POST /api/v1/todos {"title":"T","categoryId":1}` → `201` with `categoryName:"Work"`.
- `DELETE /api/v1/categories/1` → `204`; `GET /api/v1/todos/1` → `categoryId: null`.

### Breaking Changes
- `TodoResponse` gains `categoryId` and `categoryName` fields — additive, not breaking.
- `TodoService` constructor signature changes (adds `category_repository`) — internal only, no public API break.

---

## Phase 4 — Update & Expand Tests, Add Failing Edge Cases, Resolve Failures

### Feature Summary
Expand test suite to cover Category CRUD and the category-todo relationship.
Identify and resolve any test failures introduced by Phase 3 changes.
No new application features.

### Database Changes
None.

### API Contract
No new endpoints.

### Backend Implementation

**Files to create**:

| # | Path | Purpose |
|---|------|---------|
| 1 | `api/tests/test_category_repository.py` | Repository tests |
| 2 | `api/tests/test_category_service.py` | Service tests with mocked repo |
| 3 | `api/tests/test_category_routes.py` | Route integration tests |

**Files to update**:

| Path | Additions |
|------|-----------|
| `api/tests/test_todo_service.py` | 3 new test cases for category_id validation |
| `api/tests/test_todo_routes.py` | 3 new test cases for category_id in payloads |
| `api/tests/conftest.py` | Add fixtures for seeded Category objects |

**`test_category_repository.py` — test cases**:

| Test Name | Assertion |
|-----------|-----------|
| `test_get_all_returns_empty_list` | Returns `[]` |
| `test_get_all_returns_all_categories` | Returns all seeded categories |
| `test_get_by_id_returns_category` | Correct `Category` object returned |
| `test_get_by_id_returns_none_when_not_found` | Returns `None` |
| `test_get_by_name_returns_category` | Correct object by name |
| `test_get_by_name_returns_none_when_not_found` | Returns `None` |
| `test_create_returns_category_with_id` | `id` populated after flush |
| `test_update_returns_updated_category` | `name` reflects new value |
| `test_delete_returns_true_on_success` | Returns `True`, category gone |
| `test_delete_sets_todos_category_id_to_null` | After category delete, associated todo has `category_id = None` |

**`test_category_service.py` — test cases**:

| Test Name | Assertion |
|-----------|-----------|
| `test_get_all_returns_list` | Delegates to repo |
| `test_get_by_id_returns_category` | Returns category |
| `test_get_by_id_raises_404_when_not_found` | `HTTPException` 404 |
| `test_create_returns_category` | Calls repo.create, commits |
| `test_create_raises_409_on_duplicate_name` | `HTTPException` 409 with correct detail |
| `test_update_returns_updated_category` | Commits on success |
| `test_update_raises_404_when_not_found` | `HTTPException` 404 |
| `test_delete_success` | Commits on success |
| `test_delete_raises_404_when_not_found` | `HTTPException` 404 |

**`test_category_routes.py` — test cases**:

| Test Name | Expected Status |
|-----------|----------------|
| `test_create_category_returns_201` | `201` + `id` in body |
| `test_create_category_returns_409_on_duplicate_name` | `409` + `"detail"` key |
| `test_create_category_returns_422_on_missing_name` | `422` |
| `test_list_categories_returns_200` | `200` + array |
| `test_get_category_returns_200` | `200` |
| `test_get_category_returns_404` | `404` |
| `test_update_category_returns_200` | `200` + updated field |
| `test_update_category_returns_404` | `404` |
| `test_delete_category_returns_204` | `204` + empty body |
| `test_delete_category_returns_404` | `404` |

**Additional `test_todo_service.py` cases**:

| Test Name | Assertion |
|-----------|-----------|
| `test_create_todo_with_valid_category_id_succeeds` | Returns todo with `category_id` set |
| `test_create_todo_with_invalid_category_id_raises_404` | `HTTPException` 404 |
| `test_update_todo_with_category_id_succeeds` | Returns updated todo with `category_id` |

**Additional `test_todo_routes.py` cases**:

| Test Name | Expected Status |
|-----------|----------------|
| `test_create_todo_with_category_id_returns_201` | `201` + `categoryId` in body |
| `test_create_todo_with_invalid_category_id_returns_404` | `404` |
| `test_todo_response_includes_category_name` | `categoryName` field in body equals seeded category name |

### Frontend Implementation

**Files to create**:

| # | Path | Purpose |
|---|------|---------|
| 1 | `web/src/components/CategoryBadge.test.tsx` | RTL tests |
| 2 | `web/src/components/CategorySelect.test.tsx` | RTL tests |

**`CategoryBadge.test.tsx` — test cases**:

| Test Name | Assertion |
|-----------|-----------|
| `test renders category name` | Name text visible in DOM |
| `test renders nothing when category is null` | Component returns `null`, no DOM node |

**`CategorySelect.test.tsx` — test cases**:

| Test Name | Assertion |
|-----------|-----------|
| `test renders loading state` | Loading indicator visible when `useCategories` returns `isLoading: true` |
| `test renders category options` | Each category name appears as an `<option>` |
| `test calls onChange with category id when option selected` | `onChange` called with correct `id` |
| `test shows placeholder when no category is selected` | "No category" option visible and selected |

**Mocking pattern**:
```typescript
vi.mock('@/hooks/useCategories', () => ({
  useCategories: vi.fn(),
}));
```

### Copilot Agent Mode Prompts

```
1. @api Create api/tests/test_category_repository.py covering all CategoryRepository
   methods using the async_session fixture. Include a test that seeds a Category and
   an associated Todo, deletes the Category, then asserts todo.category_id is None.

2. @api Create api/tests/test_category_service.py. Mock CategoryRepository with AsyncMock.
   Test 409 on duplicate name (mock get_by_name returns a Category).
   Test 404 on not found for get_by_id, update, delete.

3. @api Create api/tests/test_category_routes.py using the client fixture.
   Test all 5 endpoints. For 409: seed a category first, then send duplicate name.
   Assert "detail" key in 409 and 404 responses.

4. @api Update api/tests/test_todo_service.py: add tests for category_id validation.
   Mock both TodoRepository and CategoryRepository. Test that invalid category_id raises 404.

5. @api Update api/tests/test_todo_routes.py: add tests that create a category first,
   then create a todo with categoryId. Assert categoryName in response. Also test
   invalid categoryId returns 404.

6. @api Run pytest -v. For every failing test, identify the root cause in source code
   and fix it (never modify tests). Re-run until all tests pass.

7. @web Create CategoryBadge.test.tsx: test renders name, test returns null when null prop.
   Create CategorySelect.test.tsx: mock useCategories, test all four states with userEvent.

8. @web Run vitest run. For every failing test, fix source code. Re-run until all pass.
```

### Testing Plan
- `cd api && pytest -v` → all tests pass (Phase 2 tests + ~20 new Category tests).
- `cd web && vitest run` → all tests pass (Phase 2 tests + 6 new Category tests).

### Breaking Changes
None — purely additive test coverage.

---

## Phase 5 — Final Integration Run + Security Review

### Feature Summary
Full test suite execution, PR review prompt checklist pass, and OWASP Top 10
security audit. Fixes only — no new features.

### Database Changes
None.

### API Contract
No new endpoints.

### Backend Implementation
No new files. Source code fixes only based on findings.

**Security audit checklist** (review every file in `api/`):

| Check | Tool / How |
|-------|-----------|
| No hardcoded secrets or connection strings | `grep -r "sa:" api/app/` — must return nothing |
| CORS uses explicit origin list from env | Verify `CORSMiddleware(allow_origins=settings.ALLOWED_ORIGINS)` |
| All string inputs validated by Pydantic `Field` | Inspect all schemas for `min_length`, `max_length` |
| No raw SQL (`text()` or string concat) | `grep -r "text(" api/app/` — must return nothing |
| Error responses omit stack traces | FastAPI default; verify no `exception_handlers` that expose `str(exc)` |
| No `bare except:` clauses | `grep -r "except:" api/` — must return nothing |
| No `# type: ignore` without comment | `grep -r "type: ignore" api/` — each must have explanation after |
| `.env` not committed | `git ls-files api/.env` — must return nothing |
| Logging excludes sensitive data | Inspect `logger.*` calls; no passwords or full connection strings |
| All DB operations awaited | `grep -rn "await" api/app/repositories/` — every query is awaited |

**PR review checklist** (from `pr-review.prompt.md`):

| Section | Items |
|---------|-------|
| Architecture Compliance | Routes → Services → Repos only; no cross-layer leaks |
| Type Safety | Full type hints; no `# type: ignore` without comment |
| Security | No secrets; all input validated; no raw SQL; CORS not wildcard; no stack traces in errors |
| Async Correctness | All DB ops awaited; no blocking I/O |
| Error Handling | Correct status codes; specific exceptions; all `isLoading`/`isError` handled |
| Database | No `create_all()`; Alembic for all changes; migration has `upgrade` + `downgrade` |
| Test Coverage | Every public function tested; edge cases covered |

### Frontend Implementation
No new files. Source code fixes only.

**Security audit checklist** (review every file in `web/src/`):

| Check | How |
|-------|-----|
| No hardcoded API base URLs | `grep -r "localhost:8000" web/src/` — must return nothing |
| No `any` type | `grep -r ": any" web/src/` — must return nothing |
| No `@ts-ignore` without comment | `grep -r "@ts-ignore" web/src/` — each must have explanation |
| No `console.log` in production | `grep -r "console.log" web/src/` — must return nothing (or be commented as intentional debug) |
| No `dangerouslySetInnerHTML` | `grep -r "dangerouslySetInnerHTML" web/src/` — must return nothing |
| `.env` not committed | `git ls-files web/.env` — must return nothing |
| All React Query mutations call `invalidateQueries` on success | Inspect all `useMutation` hooks |

### Copilot Agent Mode Prompts

```
1. @api Run pytest -v and show the full output. Fix any failures in source code
   (never in tests) and re-run until all tests pass with 0 failures, 0 errors.

2. @web Run vitest run and show the full output. Fix any failures in source code
   (never in tests) and re-run until all tests pass with 0 failures.

3. Use the #pr-review prompt to run the full code review checklist against all
   changed files in this project. Report each checklist item as ✅ or ❌ with
   a one-line description. Fix all ❌ findings immediately.

4. @api Perform a security review of all files in api/app/:
   - Verify CORSMiddleware uses allow_origins from Settings (not "*").
   - Verify all Pydantic schemas have Field constraints on string inputs.
   - Verify no raw SQL text() calls in repositories.
   - Verify error detail messages don't expose exception class names or stack traces.
   - Verify .env is not tracked by git.
   Fix any issues found.

5. @web Perform a security review of all files in web/src/:
   - Verify no hardcoded URLs (baseURL must come from import.meta.env).
   - Verify no `any` types.
   - Verify no console.log in production paths.
   - Verify no dangerouslySetInnerHTML.
   Fix any issues found.

6. Use the #commit-message prompt to generate the final commit message for all
   staged changes.
```

### Testing Plan

**Final acceptance gate — all must pass before the project is considered complete**:

| Command | Expected Result |
|---------|----------------|
| `cd api && pytest -v` | 0 failures, 0 errors |
| `cd web && vitest run` | 0 failures |
| PR review prompt | All checklist items ✅ |
| Security grep checks | All return empty (no findings) |

### Breaking Changes
None — Phase 5 is hardening and verification only.
