# Copilot Customization Guide — Todo AI Project

## How Copilot Customization Works

VS Code Copilot uses a layered system of files to understand your project, follow your rules, and respond to your commands. This guide explains **what each file does**, **when it activates**, and **how to use it** during development.

---

## 1. Custom Instructions (Always Active — Automatic)

> These files are **automatically loaded** into every Copilot interaction. You never need to reference them — they silently shape all AI responses.

| File | Scope | Role |
|---|---|---|
| `copilot-instructions.md` | Entire workspace | Defines architecture rules, coding standards, and conventions for both backend and frontend |
| `instructions/api.instructions.md` | `api/**/*.py` files only | Python-specific rules: async patterns, SQLAlchemy 2.x syntax, type hints, logging, layer boundaries |
| `instructions/web.instructions.md` | `web/src/**/*.{ts,tsx}` files only | React/TypeScript rules: strict types, React Query patterns, named exports, component structure |

### When They Activate
- **Every time** you open Copilot Chat, use inline completions, or run Agent mode while editing files matching the scope
- No action required from you — they are injected automatically

### Use Case Examples
```
┌─────────────────────────────────────────────────────────────────┐
│ You are editing api/app/services/todo_service.py                │
│                                                                 │
│ Copilot automatically loads:                                    │
│   ✅ copilot-instructions.md      (always)                     │
│   ✅ instructions/api.instructions.md  (matches api/**/*.py)   │
│   ❌ instructions/web.instructions.md  (does not match)        │
│                                                                 │
│ Result: Copilot knows to use async def, type hints, and will   │
│ NOT put SQLAlchemy queries in the service layer.                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ You are editing web/src/hooks/useTodos.ts                       │
│                                                                 │
│ Copilot automatically loads:                                    │
│   ✅ copilot-instructions.md      (always)                     │
│   ❌ instructions/api.instructions.md  (does not match)        │
│   ✅ instructions/web.instructions.md  (matches web/src/**)    │
│                                                                 │
│ Result: Copilot uses React Query, strict TypeScript, and will  │
│ NOT call Axios directly from components.                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Custom Agents (Invoke with @agent-name)

> Agents are **scoped AI assistants** that only see specific parts of the codebase. Use them to get focused, context-aware responses.

| Agent | File | Codebase Scope | When to Use |
|---|---|---|---|
| `@api` | `.vscode/agents/api-agent.agent.yml` | `api/**` | Any backend task: models, routes, services, repositories, DB |
| `@web` | `.vscode/agents/web-agent.agent.yml` | `web/**` | Any frontend task: components, hooks, services, pages |

### How to Use
Type `@api` or `@web` in Copilot Chat (Agent mode) before your prompt:

```
@api Create the TodoRepository with async CRUD methods for the todos table

@web Create a useTodos hook that fetches all todos using React Query
```

### Use Case — Parallel Backend + Frontend Development
```
Phase 1: Basic Todo CRUD
├── Backend (use @api agent)
│   ├── @api Create the Todo SQLAlchemy model with id, title, description, is_completed
│   ├── @api Create Pydantic schemas for Todo create/update/response
│   ├── @api Create TodoRepository with get_all, get_by_id, create, update, delete
│   ├── @api Create TodoService with business logic calling the repository
│   └── @api Create todo_router with GET/POST/PUT/DELETE endpoints
│
└── Frontend (use @web agent)
    ├── @web Create Todo TypeScript interfaces matching the API response
    ├── @web Create todoService.ts with Axios calls for all CRUD endpoints
    ├── @web Create useTodos.ts hook wrapping todoService with React Query
    └── @web Create TodoList page component that displays and manages todos
```

---

## 3. Prompt Files (Invoke with #prompt-name)

> Prompt files are **reusable command templates** you invoke on demand. They contain structured instructions for specific tasks.

| Prompt | File | Purpose | When to Use |
|---|---|---|---|
| `#generate-prd` | `prompts/generate-prd.prompt.md` | Generate a Product Requirements Document | Before starting any new feature — defines WHAT to build |
| `#generate-trd` | `prompts/generate-trd.prompt.md` | Generate a Technical Requirements Document | After PRD approval — defines HOW to build it |
| `#commit-message` | `prompts/commit-message.prompt.md` | Generate conventional commit message | After staging changes, before committing |
| `#pr-review` | `prompts/pr-review.prompt.md` | Run pre-PR code review checklist | Before creating a Pull Request — quality gate |
| `#db-migration` | `prompts/db-migration.prompt.md` | Generate and review Alembic migration | After any model change — Phase 1 and Phase 3 |

### How to Use
Type `#prompt-name` in Copilot Chat to invoke:

```
#generate-prd Create a PRD for the basic Todo CRUD feature

#generate-trd Based on the Todo CRUD PRD, create the technical implementation plan

#commit-message

#pr-review

#db-migration
```

### Use Case — Feature Development Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                 FEATURE DEVELOPMENT LIFECYCLE                │
│                                                              │
│  Step 1: PLAN                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ #generate-prd                                        │    │
│  │ "Create PRD for Todo CRUD with create, read, update, │    │
│  │  delete, and mark-as-complete functionality"          │    │
│  └──────────────────┬───────────────────────────────────┘    │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ #generate-trd                                        │    │
│  │ "Based on the PRD above, create the TRD with         │    │
│  │  implementation steps and Copilot prompts"            │    │
│  └──────────────────┬───────────────────────────────────┘    │
│                     ▼                                        │
│  Step 2: BUILD (using @api and @web agents)                  │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Execute each Copilot prompt from the TRD             │    │
│  │ @api ... → @web ... → @api ... → @web ...            │    │
│  └──────────────────┬───────────────────────────────────┘    │
│                     ▼                                        │
│  Step 3: MIGRATE                                             │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ #db-migration                                        │    │
│  │ Reviews models, generates Alembic migration,         │    │
│  │ checks for data loss, applies to DB                   │    │
│  └──────────────────┬───────────────────────────────────┘    │
│                     ▼                                        │
│  Step 4: COMMIT                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ git add <files>                                      │    │
│  │ #commit-message                                      │    │
│  │ → generates: "feat(api): add todo CRUD endpoints     │    │
│  │    with 3-layer architecture"                         │    │
│  └──────────────────┬───────────────────────────────────┘    │
│                     ▼                                        │
│  Step 5: REVIEW & PR                                         │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ #pr-review                                           │    │
│  │ → ✅ Architecture compliance                         │    │
│  │ → ✅ Type safety                                     │    │
│  │ → ✅ Error handling                                   │    │
│  │ → ❌ Tests missing (fix before PR)                   │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Agent Skills (Auto-Triggered — Automatic)

> Skills **automatically activate** when Copilot detects matching keywords in your prompt. You don't invoke them — they inject extra instructions behind the scenes.

| Skill | File | Triggers On | Role |
|---|---|---|---|
| **commit-message** | `skills/commit-message.skill.yml` | "generate commit", "commit message" | Enforces Conventional Commits format |
| **code-review** | `skills/code-review.skill.yml` | "review code", "code review", "pre-pr check" | Runs architecture + quality checklist |
| **test-generator** | `skills/test-generator.skill.yml` | "generate tests", "write tests", "add tests" | Enforces pytest-asyncio / vitest patterns |
| **security-review** | `skills/security-review.skill.yml` | "security review", "security check", "owasp review" | Checks OWASP Top 10 vulnerabilities |

### How They Work
You just write naturally — the skill activates when your prompt contains trigger words:

```
"Write tests for the TodoService"
       ^^^^^
       Triggers: test-generator skill
       Result: Copilot follows pytest-asyncio patterns, creates fixtures,
               tests happy path + edge cases + error cases

"Do a security review of the api folder"
        ^^^^^^^^^^^^^^^
        Triggers: security-review skill
        Result: Copilot checks for injection, XSS, exposed secrets,
                CORS config, input validation — outputs PASS/WARN/FAIL
```

### Use Case — Phase-Specific Skill Usage

```
Phase 2 (Tests):
  "Generate tests for TodoRepository"    → test-generator activates
  "Write tests for the todo hooks"       → test-generator activates
  "Add tests for the create endpoint"    → test-generator activates

Phase 4 (Expanded Tests):
  "Add failing edge case tests for empty title validation"
                                         → test-generator activates

Phase 5 (Security):
  "Run a security review on the entire codebase"
                                         → security-review activates
  "Check for OWASP vulnerabilities in the API"
                                         → security-review activates
```

---

## 5. Quick Reference — What to Use When

| I want to... | Use | How |
|---|---|---|
| Get architecture-aware code suggestions | Custom Instructions | Automatic — just code |
| Work on backend only | `@api` agent | Type `@api` before prompt |
| Work on frontend only | `@web` agent | Type `@web` before prompt |
| Plan a new feature | `#generate-prd` then `#generate-trd` | Type in Chat |
| Generate a commit message | `#commit-message` | Stage changes, then type in Chat |
| Review code before PR | `#pr-review` | Type in Chat on feature branch |
| Generate a DB migration | `#db-migration` | Type in Chat after model changes |
| Write tests | Just say "write tests" | test-generator skill auto-activates |
| Security audit | Just say "security review" | security-review skill auto-activates |

---

## 6. File Tree — All Copilot Artifacts

```
.github/
├── copilot-instructions.md              ← Always active (workspace-wide rules)
├── instructions/
│   ├── api.instructions.md              ← Auto-scoped to api/**/*.py
│   └── web.instructions.md              ← Auto-scoped to web/src/**/*.{ts,tsx}
├── prompts/
│   ├── generate-prd.prompt.md           ← #generate-prd (on demand)
│   ├── generate-trd.prompt.md           ← #generate-trd (on demand)
│   ├── commit-message.prompt.md         ← #commit-message (on demand)
│   ├── pr-review.prompt.md              ← #pr-review (on demand)
│   └── db-migration.prompt.md           ← #db-migration (on demand)
└── skills/
    ├── commit-message.skill.yml         ← Auto-triggers on "commit message"
    ├── code-review.skill.yml            ← Auto-triggers on "review code"
    ├── test-generator.skill.yml         ← Auto-triggers on "write tests"
    └── security-review.skill.yml        ← Auto-triggers on "security review"

.vscode/
└── agents/
    ├── api-agent.agent.yml              ← @api (invoke in Chat)
    └── web-agent.agent.yml              ← @web (invoke in Chat)
```

---

## 7. Phase-by-Phase Usage Map

| Phase | Agents | Prompts | Skills |
|---|---|---|---|
| **Phase 0** — Foundation | — | — | — |
| **Phase 1** — Todo CRUD | `@api`, `@web` | `#generate-prd`, `#generate-trd`, `#db-migration`, `#commit-message` | commit-message |
| **Phase 2** — Unit Tests | `@api`, `@web` | `#commit-message` | **test-generator** |
| **Phase 3** — Categories | `@api`, `@web` | `#generate-prd`, `#generate-trd`, `#db-migration`, `#commit-message` | commit-message |
| **Phase 4** — Expand Tests | `@api`, `@web` | `#commit-message` | **test-generator** |
| **Phase 5** — Integration & Security | `@api`, `@web` | `#pr-review`, `#commit-message` | **security-review** |

---

## 8. RTACCO Pattern — Used in All Major Prompts

Every prompt file follows the **RTACCO** structure for consistent, high-quality AI output:

```
R — Role        : Who is the AI acting as? (e.g., Senior Product Manager)
T — Task        : What specific output is expected?
A — Audience    : Who will read/use the output?
C — Context     : Project details, tech stack, constraints
C — Constraints : Rules, limitations, quality gates
O — Output      : Exact format and structure expected
```

This pattern is embedded in `generate-prd.prompt.md` and `generate-trd.prompt.md`. Use it when creating your own custom prompts.
