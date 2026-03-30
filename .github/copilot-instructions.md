# Project: Todo AI — Copilot Workspace Instructions

## Architecture
- Monorepo: /api (Python FastAPI backend), /web (React TypeScript frontend)
- 3-layer backend: Routes → Services → Repositories
- Routes: no business logic, no direct DB access
- Services: all business rules, calls repositories, raises HTTPException
- Repositories: pure SQLAlchemy queries, no business logic, no HTTP knowledge
- Dependency injection via FastAPI Depends() chain: get_db → Repository → Service → Route

## Backend Standards
- Python 3.11+, FastAPI, SQLAlchemy 2.x async, Pydantic v2
- All repository and service methods must be async def
- Use AsyncSession, async_sessionmaker, create_async_engine
- Database: SQL Server via aioodbc driver
- Connection string pattern: mssql+aioodbc://sa:<password>@localhost:1433/<dbname>?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes
- Every function must have a docstring and type hints
- Use logging module, never print()
- Return meaningful HTTP status codes (201 for create, 204 for delete, 404 for not found, 409 for conflict)
- Pydantic schemas for all request/response bodies — never return ORM objects directly

## Frontend Standards
- React 18, TypeScript strict mode, Vite bundler
- TanStack React Query for server state, Axios for HTTP
- Component structure: Pages → Components → Hooks → Services → Types
- All API calls go through /web/src/services/ (Axios client layer)
- All server state access goes through /web/src/hooks/ (React Query hooks)
- Components never call Axios directly

## General
- No authentication required (single-user app)
- Every file should have clear inline comments for complex logic
- No secrets in code — use environment variables
- Commit messages follow Conventional Commits (feat:, fix:, chore:, docs:)
