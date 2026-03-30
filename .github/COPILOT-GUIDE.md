# Copilot Customization Guide — Todo AI Project

> A complete reference for understanding and using every GitHub Copilot
> customization artifact in this project. Read this before writing your
> first line of code.

---

## Table of Contents

1. [The Big Picture — How Copilot Customization Works](#1-the-big-picture)
2. [Custom Instructions — The Silent Rules](#2-custom-instructions)
3. [Custom Agents — Scoped AI Assistants](#3-custom-agents)
4. [Prompt Files — Reusable Command Templates](#4-prompt-files)
5. [Agent Skills — Auto-Triggered Capabilities](#5-agent-skills)
6. [Quick Reference — What to Use When](#6-quick-reference)
7. [File Tree — Complete Artifact Layout](#7-file-tree)
8. [Phase-by-Phase Usage Map](#8-phase-by-phase-usage-map)
9. [RTACCO Pattern — Prompt Engineering Framework](#9-rtacco-pattern)

---

## 1. The Big Picture

GitHub Copilot in VS Code supports **four customization primitives**. Each one
controls AI behavior in a different way:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COPILOT CUSTOMIZATION STACK                         │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │  LAYER 4: SKILLS (.github/skills/*.skill.yml)                │     │
│  │  Behavior: AUTO-TRIGGERED — activates when keywords appear   │     │
│  │  Purpose:  Inject domain-specific rules into any prompt      │     │
│  │  You say:  "write tests" → skill silently loads test rules   │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │  LAYER 3: PROMPT FILES (.github/prompts/*.prompt.md)         │     │
│  │  Behavior: ON-DEMAND — you invoke with #prompt-name          │     │
│  │  Purpose:  Reusable templates for recurring tasks            │     │
│  │  You say:  #generate-prd → Copilot runs the full PRD prompt  │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │  LAYER 2: CUSTOM AGENTS (.vscode/agents/*.agent.yml)         │     │
│  │  Behavior: ON-DEMAND — you invoke with @agent-name           │     │
│  │  Purpose:  Scope AI to specific folders in the codebase      │     │
│  │  You say:  @api create the Todo model → only sees api/**     │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │  LAYER 1: CUSTOM INSTRUCTIONS (.github/**instructions.md)    │     │
│  │  Behavior: ALWAYS ACTIVE — loaded automatically, every time  │     │
│  │  Purpose:  Set project-wide and language-specific rules      │     │
│  │  You do:   Nothing — they just work                          │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                       │
│  KEY INSIGHT:                                                         │
│  Layers 1 + 4 are AUTOMATIC (you never invoke them)                   │
│  Layers 2 + 3 are MANUAL    (you invoke them with @ or #)             │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why does this matter?

Without customization, Copilot generates generic code. With it:
- It **follows your architecture** (3-layer backend, React Query frontend)
- It **uses your conventions** (async/await, Pydantic v2, named exports)
- It **avoids anti-patterns** (no Axios in components, no SQL in services)
- It **enforces quality gates** (tests follow your structure, reviews check your rules)

---

## 2. Custom Instructions — The Silent Rules

### What Are They?

Custom Instructions are markdown files that Copilot reads **automatically**
before generating any response. You never reference them — they are injected
silently into every Copilot interaction based on file scope.

### The Three Instruction Files

#### File 1: `copilot-instructions.md` — The Global Rulebook

```
Location:  .github/copilot-instructions.md
Scope:     ENTIRE WORKSPACE — every file, every language, every interaction
Loaded:    Always, automatically
```

**What it contains:**
- Architecture definition (monorepo, 3-layer backend, component structure)
- Backend standards (async, type hints, logging, HTTP status codes)
- Frontend standards (React Query, Axios service pattern, strict TypeScript)
- General rules (no auth, env vars for secrets, conventional commits)

**What it prevents:**
- Copilot generating a route that queries the database directly
- Copilot using `print()` instead of `logging`
- Copilot returning ORM objects from API endpoints (must use Pydantic schemas)
- Copilot using default exports in React components

#### File 2: `api.instructions.md` — Python/Backend Rules

```
Location:  .github/instructions/api.instructions.md
Scope:     api/**/*.py  (only Python files inside the api/ folder)
Loaded:    Only when you're working on backend files
```

**What it contains:**
- Python 3.11+ syntax requirements
- SQLAlchemy 2.x patterns (`Mapped`, `mapped_column`, not legacy `Column`)
- Import ordering rules (stdlib → third-party → local)
- Layer-specific rules (HTTPException only in Services, not Repositories)
- Logging pattern (`logger = logging.getLogger(__name__)`)

**What it prevents:**
- Copilot using `Column(Integer)` instead of `Mapped[int]`
- Copilot adding a bare `except:` without specifying the exception type
- Copilot raising `HTTPException` inside a repository method
- Copilot forgetting `async def` on database operations

#### File 3: `web.instructions.md` — React/TypeScript Rules

```
Location:  .github/instructions/web.instructions.md
Scope:     web/src/**/*.{ts,tsx}  (only TS/TSX files inside web/src/)
Loaded:    Only when you're working on frontend files
```

**What it contains:**
- Strict TypeScript mode enforcement (no `any`)
- React Query as the only server state manager
- Hook-per-domain pattern (`useTodos.ts`, `useCategories.ts`)
- Named exports over default exports
- Axios instance via service layer only

**What it prevents:**
- Copilot using `useState` to store API response data
- Copilot calling `axios.get()` directly inside a component
- Copilot using `export default` on components
- Copilot using `any` type assertions

### How Scope Matching Works — Visual Walkthrough

```
SCENARIO A: You open api/app/services/todo_service.py and ask Copilot a question

  Copilot checks:
  ┌──────────────────────────────────────────────────────────────────┐
  │ File being edited: api/app/services/todo_service.py              │
  │                                                                  │
  │ copilot-instructions.md         → scope: *         → LOADED     │
  │ instructions/api.instructions.md → scope: api/**/*.py → LOADED  │
  │ instructions/web.instructions.md → scope: web/src/** → SKIPPED  │
  │                                                                  │
  │ Copilot now knows:                                               │
  │  - This is a SERVICE file (business logic layer)                 │
  │  - Must use async def with type hints                            │
  │  - Can raise HTTPException here                                  │
  │  - Must NOT write SQLAlchemy queries here                        │
  │  - Must call repository methods instead                          │
  └──────────────────────────────────────────────────────────────────┘

SCENARIO B: You open web/src/hooks/useTodos.ts and ask Copilot a question

  Copilot checks:
  ┌──────────────────────────────────────────────────────────────────┐
  │ File being edited: web/src/hooks/useTodos.ts                     │
  │                                                                  │
  │ copilot-instructions.md         → scope: *         → LOADED     │
  │ instructions/api.instructions.md → scope: api/**/*.py → SKIPPED │
  │ instructions/web.instructions.md → scope: web/src/** → LOADED   │
  │                                                                  │
  │ Copilot now knows:                                               │
  │  - This is a HOOK file (React Query wrapper)                     │
  │  - Must use useQuery/useMutation from TanStack                   │
  │  - Must call service functions, not Axios directly               │
  │  - Must use strict TypeScript types, no 'any'                    │
  │  - Must use named export                                         │
  └──────────────────────────────────────────────────────────────────┘

SCENARIO C: You open .github/prompts/commit.prompt.md (not in any scope)

  Copilot checks:
  ┌──────────────────────────────────────────────────────────────────┐
  │ File being edited: .github/prompts/commit.prompt.md              │
  │                                                                  │
  │ copilot-instructions.md         → scope: *         → LOADED     │
  │ instructions/api.instructions.md → scope: api/**/*.py → SKIPPED │
  │ instructions/web.instructions.md → scope: web/src/** → SKIPPED  │
  │                                                                  │
  │ Only the global instructions apply here.                         │
  └──────────────────────────────────────────────────────────────────┘
```

### Key Takeaway

> You never type anything to activate these files. They are the **foundation**
> that makes every other Copilot feature work correctly in this project.
> Without them, Copilot would generate generic Python/React code that
> ignores your architecture.

---

## 3. Custom Agents — Scoped AI Assistants

### What Are They?

Custom Agents are **named AI personas** that only see a subset of your codebase.
When you use `@api`, Copilot only indexes files under `api/`. When you use
`@web`, it only indexes files under `web/`. This makes responses faster,
more focused, and less likely to confuse backend and frontend code.

### The Two Agents

#### `@api` — Backend Expert

```
File:       .vscode/agents/api-agent.agent.yml
Sees:       api/** (all backend files)
Cannot see: web/** (frontend is invisible to this agent)
Persona:    Expert Python/FastAPI developer
Knows:      3-layer architecture, async SQLAlchemy, Pydantic v2, SQL Server
```

#### `@web` — Frontend Expert

```
File:       .vscode/agents/web-agent.agent.yml
Sees:       web/** (all frontend files)
Cannot see: api/** (backend is invisible to this agent)
Persona:    Expert React/TypeScript developer
Knows:      React Query, Axios service pattern, component architecture, Vite
```

### How to Use — Syntax

In VS Code Copilot Chat (Agent mode panel), type `@` followed by the agent name:

```
@api <your prompt here>
@web <your prompt here>
```

### When to Use Each Agent

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DECISION TREE                                  │
│                                                                       │
│  "What am I building right now?"                                      │
│                                                                       │
│  ├─ Database model, migration, or schema?          → Use @api         │
│  ├─ API endpoint, service, or repository?          → Use @api         │
│  ├─ React component, page, or layout?              → Use @web         │
│  ├─ React Query hook or Axios service function?    → Use @web         │
│  ├─ TypeScript types that mirror API response?     → Use @web         │
│  ├─ Something that spans both (e.g., full feature)?                   │
│  │   → Break it into two prompts: one @api, one @web                  │
│  └─ Config file (.env, vite.config, alembic.ini)?  → Use @workspace   │
└────────────────────────────────────────────────────────────────────────┘
```

### Real-World Example — Building a Feature with Both Agents

```
Step 1 — Backend first (because frontend depends on the API contract):

  @api Create the Todo SQLAlchemy model in app/models/todo.py with columns:
  id (int, primary key, auto-increment), title (str, max 200, not null),
  description (str, nullable), is_completed (bool, default false),
  created_at (datetime, server default now), updated_at (datetime, on update now)

Step 2 — Still backend:

  @api Create TodoRepository in app/repositories/todo_repository.py with async
  methods: get_all, get_by_id, create, update, delete. Each method takes
  AsyncSession as first parameter via dependency injection.

Step 3 — Switch to frontend:

  @web Create the Todo TypeScript interface in web/src/types/index.ts matching
  the API response shape: id, title, description, is_completed, created_at,
  updated_at

Step 4 — Still frontend:

  @web Create todoService.ts in web/src/services/ with Axios functions:
  getTodos, getTodoById, createTodo, updateTodo, deleteTodo.
  Use the api instance from services/api.ts.
```

### Why Not Just Use @workspace for Everything?

| Approach | Pros | Cons |
|---|---|---|
| `@workspace` | Sees everything | Slower, may confuse backend/frontend patterns |
| `@api` | Fast, focused, backend-expert persona | Cannot help with frontend |
| `@web` | Fast, focused, frontend-expert persona | Cannot help with backend |

**Rule of thumb:** Use `@api` or `@web` for implementation. Use `@workspace`
only for cross-cutting concerns (CI/CD, documentation, config files).

---

## 4. Prompt Files — Reusable Command Templates

### What Are They?

Prompt files are **pre-written, structured prompts** saved as markdown files.
Instead of typing a complex prompt from scratch every time, you invoke it
by name. Think of them as **macros** or **stored procedures** for AI prompts.

### How to Invoke

In Copilot Chat, type `#` followed by the prompt file name:

```
#generate-prd
#generate-trd
#commit-message
#pr-review
#db-migration
```

You can also add additional context after the prompt name:

```
#generate-prd Create a PRD for adding category labels to todos
#db-migration Check for any pending model changes after adding the category table
```

### The Five Prompt Files — Detailed Breakdown

---

#### `#generate-prd` — Product Requirements Document

```
File:     .github/prompts/generate-prd.prompt.md
Purpose:  Define WHAT to build before writing any code
When:     At the START of every new feature (Phase 1, Phase 3)
Output:   Feature title, problem statement, user stories,
          acceptance criteria (Given/When/Then), out of scope
```

**Why it matters:**
Starting with a PRD forces you to think about the user experience before
diving into implementation. Copilot uses the RTACCO pattern inside this
prompt to act as a Senior Product Manager.

**Example usage:**
```
#generate-prd

Feature: Basic Todo CRUD
Users need to create, view, edit, delete, and mark todos as complete.
The app is single-user, no auth required.
```

**What Copilot produces:**
```markdown
## Feature Title: Basic Todo Management

## Problem Statement
Users need a way to track tasks with the ability to create, view,
update, delete, and mark items as complete.

## User Stories
- As a user, I want to create a todo with a title and optional
  description so that I can track tasks.
- As a user, I want to mark a todo as complete so that I can
  distinguish finished work from pending work.
...

## Acceptance Criteria
- Given I submit a title, When I click create, Then the todo
  appears in the list with is_completed=false
...
```

---

#### `#generate-trd` — Technical Requirements Document

```
File:     .github/prompts/generate-trd.prompt.md
Purpose:  Define HOW to build it — the implementation blueprint
When:     After PRD is approved, before writing code
Output:   Database changes, backend implementation plan per layer,
          frontend implementation plan per layer, Copilot prompts to execute
```

**Why it matters:**
The TRD translates product requirements into exact files, functions, and
Copilot prompts. After running this, you have a step-by-step recipe —
just execute each Copilot prompt in order.

**Example usage:**
```
#generate-trd

Based on the Todo CRUD PRD, create the technical implementation plan.
Backend uses 3-layer architecture. Frontend uses React Query hooks.
```

**What Copilot produces:**
```markdown
## Database Changes
- New table: todos (id, title, description, is_completed, created_at, updated_at)
- Migration: alembic revision --autogenerate -m "create_todos_table"

## Backend Implementation
### Models: api/app/models/todo.py
  - class Todo(Base) with Mapped columns...
### Schemas: api/app/schemas/todo.py
  - TodoCreate, TodoUpdate, TodoResponse...
...

## Copilot Agent Prompts (execute in order)
1. @api Create the Todo model...
2. @api Create the Todo schemas...
3. @api Create the TodoRepository...
...
```

---

#### `#commit-message` — Conventional Commit Generator

```
File:     .github/prompts/commit-message.prompt.md
Purpose:  Generate a standardized commit message from staged changes
When:     After running git add, before git commit
Output:   A single commit message in Conventional Commits format
```

**How it works:**
1. You stage your changes: `git add api/app/models/todo.py`
2. You invoke: `#commit-message`
3. Copilot reads `git diff --cached` and generates:
   `feat(api): add Todo SQLAlchemy model with CRUD-ready columns`
4. You run: `git commit -m "<the generated message>"`

**Format rules enforced by this prompt:**
```
<type>(<scope>): <summary>

Types:   feat | fix | chore | docs | test | refactor
Scope:   api | web | config | db | <module-name>
Summary: imperative mood, lowercase, no period, max 72 chars

Examples:
  feat(api): add todo CRUD endpoints with 3-layer architecture
  fix(web): handle empty todo list state in TodoList component
  chore(config): update CORS origins for production deploy
  test(api): add unit tests for TodoService edge cases
  refactor(web): extract TodoItem into separate component
  docs(config): add copilot customization guide
```

---

#### `#pr-review` — Pre-PR Code Review Checklist

```
File:     .github/prompts/pr-review.prompt.md
Purpose:  Quality gate — catch issues before creating a Pull Request
When:     After all code is committed on a feature branch, before PR
Output:   A checklist with PASS/FAIL per category and explanations
```

**The 7-point checklist it runs:**

```
┌──────────────────────────────────────────────────────────────────────┐
│                     PR REVIEW CHECKLIST                              │
│                                                                      │
│  1. ARCHITECTURE COMPLIANCE                                          │
│     ├─ Routes have no business logic?                                │
│     ├─ Services have no SQLAlchemy queries?                          │
│     └─ Repositories have no HTTP knowledge?                          │
│                                                                      │
│  2. TYPE SAFETY                                                      │
│     ├─ All Python functions have type hints?                         │
│     └─ All TypeScript has strict types (no 'any')?                   │
│                                                                      │
│  3. ERROR HANDLING                                                   │
│     ├─ Proper HTTP status codes (201, 204, 404, 409)?                │
│     ├─ No bare except clauses?                                       │
│     └─ Frontend has error states/boundaries?                         │
│                                                                      │
│  4. SECURITY                                                         │
│     ├─ No secrets in code?                                           │
│     ├─ No SQL injection?                                             │
│     └─ Input validated via Pydantic / typed params?                  │
│                                                                      │
│  5. ASYNC CORRECTNESS                                                │
│     ├─ All DB operations use await?                                  │
│     └─ No sync calls blocking the async event loop?                  │
│                                                                      │
│  6. TESTS                                                            │
│     ├─ Tests exist for new code?                                     │
│     └─ Happy path + edge cases covered?                              │
│                                                                      │
│  7. DOCUMENTATION                                                    │
│     ├─ Docstrings on all public functions?                           │
│     └─ Complex logic has inline comments?                            │
└──────────────────────────────────────────────────────────────────────┘
```

**Example output from Copilot:**
```
## PR Review: feature/phase1-todo-crud → main

- [x] Architecture compliance — all layers properly separated
- [x] Type safety — full type hints on Python, strict TS
- [x] Error handling — 404 on missing todo, 201 on create
- [x] Security — no secrets, parameterized queries via ORM
- [x] Async correctness — all DB ops awaited
- [ ] Tests — NO TESTS FOUND. Add tests before merging.
- [x] Documentation — docstrings present on all public methods

VERDICT: 6/7 passing. Fix: add unit tests (Phase 2).
```

---

#### `#db-migration` — Alembic Migration Generator

```
File:     .github/prompts/db-migration.prompt.md
Purpose:  Generate, review, and apply database schema migrations
When:     After any change to files in api/app/models/
Output:   Migration command, review of generated file, apply command
```

**The 3-step process it follows:**

```
Step 1: GENERATE
  Copilot reviews app/models/*.py, compares to existing migrations,
  and outputs the command:
    alembic revision --autogenerate -m "create_todos_table"

Step 2: REVIEW
  Copilot reads the generated migration file and checks:
    - Column types map correctly to SQL Server types
    - nullable, default, index settings are correct
    - Foreign keys are properly defined
    - downgrade() properly reverses upgrade()
    - No data loss operations without warning

Step 3: APPLY
  If review passes:
    alembic upgrade head
```

---

### Prompt Files vs Skills — What's the Difference?

```
┌──────────────────────────────────────────────────────────────────────┐
│  PROMPT FILES                    │  SKILLS                          │
│  ─────────────                   │  ──────                          │
│  You invoke them (#name)         │  They invoke themselves          │
│  Run once, produce output        │  Modify how Copilot responds     │
│  Like running a script           │  Like setting environment vars   │
│  Self-contained task             │  Enhance any task                │
│                                  │                                  │
│  Example:                        │  Example:                        │
│  #commit-message                 │  "write tests for todo"          │
│  → produces a commit message     │  → skill adds testing rules      │
│  → you copy-paste and use it     │  → Copilot writes better tests   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 5. Agent Skills — Auto-Triggered Capabilities

### What Are They?

Skills are YAML files that define **trigger words** and **extra instructions**.
When Copilot detects those trigger words in your natural-language prompt,
it silently loads the skill's instructions alongside your prompt. You
**never invoke skills manually** — they activate automatically.

### How Auto-Triggering Works — Step by Step

```
YOU TYPE:
  "Write tests for the TodoService create method"

COPILOT CHECKS ALL SKILLS:
  ┌────────────────────────────────────────────────────────────────┐
  │  commit-message.skill.yml                                      │
  │    triggers: "generate commit", "commit message"               │
  │    match: NO                                                   │
  │                                                                │
  │  code-review.skill.yml                                         │
  │    triggers: "review code", "code review", "pre-pr check"     │
  │    match: NO                                                   │
  │                                                                │
  │  test-generator.skill.yml                                      │
  │    triggers: "generate tests", "write tests", "add tests"     │
  │    match: YES → "Write tests" matches "write tests"           │
  │    ACTION: Load test-generator instructions into context       │
  │                                                                │
  │  security-review.skill.yml                                     │
  │    triggers: "security review", "security check"              │
  │    match: NO                                                   │
  └────────────────────────────────────────────────────────────────┘

COPILOT NOW HAS:
  Your prompt:    "Write tests for the TodoService create method"
  + Skill rules:  Use pytest-asyncio, create fixtures, test happy path
                  + edge cases + error cases, mock the repository layer,
                  use descriptive test names...

RESULT:
  Copilot generates tests that follow YOUR project's testing conventions,
  not generic pytest code.
```

### The Four Skills — Detailed Breakdown

---

#### Skill: `commit-message`

```
File:      .github/skills/commit-message.skill.yml
Triggers:  "generate commit", "commit message", "write commit"
Injects:   Conventional Commits format rules, scope detection, imperative mood
```

**When it activates:**
```
"Generate a commit message for my changes"     ← triggers
"Help me write a commit for this feature"       ← triggers
"What should the commit say?"                   ← does NOT trigger (no keyword match)
```

---

#### Skill: `code-review`

```
File:      .github/skills/code-review.skill.yml
Triggers:  "review code", "code review", "pre-pr check"
Injects:   Architecture compliance checks, type safety, error handling,
           security, async correctness, test coverage, documentation rules
```

**When it activates:**
```
"Do a code review of my changes"               ← triggers
"Run a pre-pr check on this branch"             ← triggers
"Is this code good?"                            ← does NOT trigger (no keyword match)
```

---

#### Skill: `test-generator`

```
File:      .github/skills/test-generator.skill.yml
Triggers:  "generate tests", "write tests", "add tests", "create test", "unit test"
Injects:   Full testing ruleset for BOTH backend and frontend:

  Backend rules:
    - pytest + pytest-asyncio for async tests
    - File naming: test_<module>.py
    - Fixtures for sessions, test data, service/repo instances
    - Test structure: happy path, edge cases, error cases
    - Mock repository when testing services
    - Mock services when testing routes
    - Use httpx.AsyncClient for integration tests
    - Assert specific HTTP status codes

  Frontend rules:
    - vitest + @testing-library/react
    - Co-located test files: Component.test.tsx
    - Mock API services, not React Query internals
    - Test renders, loading, errors, interactions
    - Use screen queries (getByRole, getByText) over test IDs
```

**When it activates:**
```
"Write tests for TodoRepository"                ← triggers
"Generate unit tests for the create endpoint"    ← triggers
"Add tests for edge cases in todo validation"    ← triggers
"Test this function"                             ← does NOT trigger (no keyword match)
```

**What changes in Copilot's output when this skill is active:**

```
WITHOUT test-generator skill:              WITH test-generator skill:
─────────────────────────────              ────────────────────────────
def test_create():                         @pytest.mark.asyncio
    result = create("Buy milk")            async def test_create_todo_returns_
    assert result is not None                  created_todo_with_defaults(
                                               self,
                                               mock_session: AsyncSession,
                                               todo_repository: TodoRepository,
                                           ):
                                               """Creating a todo with valid title
                                               returns the todo with is_completed=False
                                               and auto-generated timestamps."""
                                               todo = await todo_repository.create(
                                                   mock_session,
                                                   TodoCreate(title="Buy milk")
                                               )
                                               assert todo.title == "Buy milk"
                                               assert todo.is_completed is False
                                               assert todo.created_at is not None
```

---

#### Skill: `security-review`

```
File:      .github/skills/security-review.skill.yml
Triggers:  "security review", "security check", "check vulnerabilities", "owasp review"
Injects:   OWASP Top 10 checklist tailored to this project's stack:

  Backend checks:
    - SQL injection (are queries via ORM, no raw string concat?)
    - Secrets exposure (.env in .gitignore? No hardcoded passwords?)
    - CORS misconfiguration (restricted to expected origins?)
    - Input validation (all bodies via Pydantic? Params typed?)
    - Error leakage (stack traces in responses?)
    - Dependency vulnerabilities (pip audit)

  Frontend checks:
    - XSS (dangerouslySetInnerHTML avoided? Input sanitized?)
    - Secrets in frontend code or committed .env?
    - CSRF (state changes use POST/PUT/DELETE, not GET?)
    - Dependency vulnerabilities (npm audit)
```

**When it activates:**
```
"Run a security review on the codebase"         ← triggers
"Check for OWASP vulnerabilities"                ← triggers
"Is the API secure?"                             ← does NOT trigger (no keyword match)
```

**Example output format:**
```
## Security Review Results

| Category              | Status | Details                            |
|---|---|---|
| SQL Injection         | PASS   | All queries via SQLAlchemy ORM      |
| Secrets Exposure      | PASS   | .env in .gitignore, no hardcoded    |
| CORS Configuration    | WARN   | Only localhost:5173 allowed — add   |
|                       |        | production origin before deploy     |
| Input Validation      | PASS   | All endpoints use Pydantic schemas  |
| XSS                   | PASS   | No dangerouslySetInnerHTML usage    |
| Dependencies (pip)    | PASS   | No known vulnerabilities            |
| Dependencies (npm)    | WARN   | 2 low-severity advisories — review  |
```

---

## 6. Quick Reference — What to Use When

### Decision Matrix

| I want to... | Type | What to Use | How |
|---|---|---|---|
| Get smart code completions | Automatic | Custom Instructions | Just code — rules auto-load |
| Build a backend feature | Manual | `@api` agent | Type `@api` + prompt in Chat |
| Build a frontend feature | Manual | `@web` agent | Type `@web` + prompt in Chat |
| Plan a new feature | Manual | `#generate-prd` | Type in Chat before coding |
| Get an implementation plan | Manual | `#generate-trd` | Type in Chat after PRD |
| Generate a commit message | Manual | `#commit-message` | Stage changes first, then type |
| Review code before PR | Manual | `#pr-review` | Type in Chat on feature branch |
| Generate a DB migration | Manual | `#db-migration` | Type in Chat after model changes |
| Write good tests | Automatic | test-generator skill | Just say "write tests" naturally |
| Run a security audit | Automatic | security-review skill | Just say "security review" |
| Generate a good commit msg | Automatic | commit-message skill | Just say "commit message" |
| Get architecture feedback | Automatic | code-review skill | Just say "review code" |

### Cheat Sheet — Common Workflows

```
NEW FEATURE:
  #generate-prd → #generate-trd → @api (build) → @web (build)
  → #db-migration → #commit-message → #pr-review

BUG FIX:
  @api or @web (diagnose + fix) → "write tests for the fix"
  → #commit-message

ADD TESTS:
  "Write tests for <module>" → test-generator auto-activates
  → #commit-message

PRE-RELEASE:
  "Security review of the codebase" → security-review auto-activates
  → #pr-review → merge
```

---

## 7. File Tree — Complete Artifact Layout

```
Todo_AI/
│
├── .github/
│   │
│   ├── copilot-instructions.md                ← ALWAYS ACTIVE
│   │   What: Global architecture + coding rules
│   │   When: Every Copilot interaction, automatically
│   │   How:  You do nothing — it just works
│   │
│   ├── instructions/
│   │   ├── api.instructions.md                ← AUTO-SCOPED to api/**/*.py
│   │   │   What: Python/FastAPI/SQLAlchemy specific rules
│   │   │   When: Only when editing backend Python files
│   │   │
│   │   └── web.instructions.md                ← AUTO-SCOPED to web/src/**
│   │       What: React/TypeScript/React Query specific rules
│   │       When: Only when editing frontend TS/TSX files
│   │
│   ├── prompts/
│   │   ├── generate-prd.prompt.md             ← INVOKE: #generate-prd
│   │   │   What: Product Requirements Document generator
│   │   │   When: Before starting any new feature
│   │   │
│   │   ├── generate-trd.prompt.md             ← INVOKE: #generate-trd
│   │   │   What: Technical Requirements Document generator
│   │   │   When: After PRD approved, before coding
│   │   │
│   │   ├── commit-message.prompt.md           ← INVOKE: #commit-message
│   │   │   What: Conventional commit message generator
│   │   │   When: After git add, before git commit
│   │   │
│   │   ├── pr-review.prompt.md                ← INVOKE: #pr-review
│   │   │   What: 7-point code review checklist
│   │   │   When: Before creating a Pull Request
│   │   │
│   │   └── db-migration.prompt.md             ← INVOKE: #db-migration
│   │       What: Alembic migration generator + reviewer
│   │       When: After any model file changes
│   │
│   └── skills/
│       ├── commit-message.skill.yml           ← AUTO-TRIGGER: "commit message"
│       │   What: Enforces Conventional Commits format
│       │
│       ├── code-review.skill.yml              ← AUTO-TRIGGER: "review code"
│       │   What: Architecture + quality checklist
│       │
│       ├── test-generator.skill.yml           ← AUTO-TRIGGER: "write tests"
│       │   What: pytest-asyncio + vitest patterns
│       │
│       └── security-review.skill.yml          ← AUTO-TRIGGER: "security review"
│           What: OWASP Top 10 vulnerability scanner
│
└── .vscode/
    └── agents/
        ├── api-agent.agent.yml                ← INVOKE: @api
        │   What: Backend-scoped AI assistant
        │   Sees:  api/** only
        │
        └── web-agent.agent.yml                ← INVOKE: @web
            What: Frontend-scoped AI assistant
            Sees:  web/** only
```

---

## 8. Phase-by-Phase Usage Map

### Which artifacts you use at each development phase:

```
PHASE 0 — Foundation & Setup
├── Created all artifacts (this phase)
├── No agents/prompts/skills used yet
└── Artifacts: ALL files created and committed

PHASE 1 — Basic Todo CRUD
├── Planning:    #generate-prd → #generate-trd
├── Backend:     @api (model → schema → repo → service → route)
├── Frontend:    @web (types → service → hook → components → page)
├── Database:    #db-migration (generate + review + apply)
├── Commit:      #commit-message
├── Review:      #pr-review (before merge to main)
└── Skills:      commit-message auto-activates

PHASE 2 — Unit Tests
├── Backend:     @api + "write tests" (test-generator activates)
├── Frontend:    @web + "write tests" (test-generator activates)
├── Commit:      #commit-message
└── Skills:      test-generator auto-activates

PHASE 3 — Add Category to Todo
├── Planning:    #generate-prd → #generate-trd
├── Backend:     @api (category model → schema → repo → service → route)
├── Frontend:    @web (category types → service → hook → UI)
├── Database:    #db-migration (new table + foreign key)
├── Commit:      #commit-message
├── Review:      #pr-review
└── Skills:      commit-message auto-activates

PHASE 4 — Expand Tests
├── Backend:     @api + "write tests" (test-generator activates)
├── Frontend:    @web + "add tests" (test-generator activates)
├── Edge cases:  "Add failing edge case tests" (test-generator activates)
├── Commit:      #commit-message
└── Skills:      test-generator auto-activates

PHASE 5 — Integration & Security
├── Security:    "Run security review" (security-review activates)
├── Review:      #pr-review (final quality gate)
├── Both:        @api + @web for any fixes
├── Commit:      #commit-message
└── Skills:      security-review + code-review auto-activate
```

---

## 9. RTACCO Pattern — Prompt Engineering Framework

### What Is RTACCO?

RTACCO is a **6-part structure** for writing prompts that produce consistent,
high-quality AI output. Every major prompt file in this project uses it.

### The Six Components

```
┌──────────────────────────────────────────────────────────────────────┐
│                         RTACCO FRAMEWORK                             │
│                                                                      │
│  R — ROLE                                                            │
│  │   WHO is the AI acting as?                                        │
│  │   Sets the expertise level and domain knowledge.                  │
│  │                                                                   │
│  │   Examples:                                                       │
│  │   - "You are a Senior Product Manager"                            │
│  │   - "You are a Software Architect with 20 years of experience"    │
│  │   - "You are a database migration specialist"                     │
│  │                                                                   │
│  │   WHY: The role determines the AI's perspective. A Product        │
│  │   Manager writes user stories; an Architect writes system design. │
│  │                                                                   │
│  T — TASK                                                            │
│  │   WHAT specific output is expected?                               │
│  │   Be explicit about the deliverable.                              │
│  │                                                                   │
│  │   Examples:                                                       │
│  │   - "Generate a Product Requirements Document"                    │
│  │   - "Create a technical implementation plan"                      │
│  │   - "Analyze staged git changes and produce a commit message"     │
│  │                                                                   │
│  │   WHY: Without a clear task, the AI may ramble or produce         │
│  │   the wrong type of output.                                       │
│  │                                                                   │
│  A — AUDIENCE                                                        │
│  │   WHO will consume this output?                                   │
│  │   Determines depth, jargon level, and format.                     │
│  │                                                                   │
│  │   Examples:                                                       │
│  │   - "Full-stack developers who will implement the feature"        │
│  │   - "A tech lead reviewing a PR"                                  │
│  │   - "A developer running git commit in the terminal"              │
│  │                                                                   │
│  │   WHY: A PRD for developers differs from a PRD for executives.   │
│  │   The audience shapes how technical the output should be.         │
│  │                                                                   │
│  C — CONTEXT                                                         │
│  │   What background information does the AI need?                   │
│  │   Tech stack, architecture, constraints, current state.           │
│  │                                                                   │
│  │   Examples:                                                       │
│  │   - "Monorepo with /api (FastAPI) and /web (React)"               │
│  │   - "3-layer architecture: Routes → Services → Repositories"     │
│  │   - "SQL Server via aioodbc async driver"                         │
│  │                                                                   │
│  │   WHY: Context prevents generic answers. The AI will generate     │
│  │   code for YOUR stack, not a generic tutorial.                    │
│  │                                                                   │
│  C — CONSTRAINTS                                                     │
│  │   What rules MUST the output follow?                              │
│  │   What must it NOT do?                                            │
│  │                                                                   │
│  │   Examples:                                                       │
│  │   - "Every file must follow layer rules — no shortcuts"           │
│  │   - "Max 72 characters for commit summary"                        │
│  │   - "Do not prescribe implementation — leave that for the TRD"    │
│  │                                                                   │
│  │   WHY: Constraints set boundaries. Without them, the AI may      │
│  │   include implementation in a PRD or skip type hints in code.     │
│  │                                                                   │
│  O — OUTPUT FORMAT                                                   │
│      What STRUCTURE should the response have?                        │
│      Headings, bullet points, code blocks, tables, checklists.       │
│                                                                      │
│      Examples:                                                       │
│      - "## Feature Title → ## User Stories → ## Acceptance Criteria" │
│      - "Output ONLY the commit message — no explanation"             │
│      - "Markdown checklist with PASS/FAIL per category"              │
│                                                                      │
│      WHY: Specifying format prevents inconsistent outputs.           │
│      You get the same structure every time you run the prompt.       │
└──────────────────────────────────────────────────────────────────────┘
```

### RTACCO in Our Prompt Files

| Prompt File | Role | Task | Key Constraint |
|---|---|---|---|
| `generate-prd` | Sr. Product Manager | PRD document | No implementation details |
| `generate-trd` | Sr. Software Architect | TRD with Copilot prompts | Must follow 3-layer arch |
| `commit-message` | (implicit) | Commit message | Max 72 chars, imperative |
| `pr-review` | (implicit) | Quality checklist | 7-point framework |
| `db-migration` | DB migration specialist | Migration + review | Check for data loss |

### How to Write Your Own Prompts Using RTACCO

If you need a new prompt file, follow this template:

```markdown
---
description: "One-line summary of what this prompt does"
---

# Role
You are a [specific expert role with relevant experience].

# Task
[Exactly what output you expect — be specific about the deliverable.]

# Audience
[Who will read/use this output and what they need from it.]

# Context
- [Tech stack details]
- [Architecture details]
- [Current project state]

# Constraints
- [What it MUST do]
- [What it must NOT do]
- [Quality requirements]

# Output Format
## [Section 1]
## [Section 2]
...
```

Save it as `.github/prompts/<name>.prompt.md` and invoke with `#<name>`.
