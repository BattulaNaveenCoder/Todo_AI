# Skill Files — Complete Guide

## 1. Introduction

### What Are Skill Files?

A **Skill File** (`SKILL.md`) is a VS Code Copilot customization primitive that packages **on-demand, domain-specific knowledge** into a self-contained folder. Each skill is a Markdown file with YAML frontmatter that tells the AI agent **what** a workflow does, **when** to activate it, and **how** to execute it step-by-step.

Think of it as a reusable "playbook" that Copilot loads only when it recognizes a relevant task — like generating API endpoints, running database migrations, or performing a security audit.

### Where and Why They Are Used

| Where | Path |
|-------|------|
| **Project-level** (shared with team) | `.github/skills/<skill-name>/SKILL.md` |
| **Project-level** (alternative locations) | `.agents/skills/<skill-name>/SKILL.md` or `.claude/skills/<skill-name>/SKILL.md` |
| **Personal** (user-level, cross-project) | `~/.copilot/skills/<skill-name>/SKILL.md` |

**Why?** Without skills, you'd repeat the same lengthy prompts every time you want Copilot to follow a specific workflow — "generate a 3-layer FastAPI endpoint with DI wiring, correct status codes, and Alembic guidance." Skills let you encode that knowledge once and invoke it automatically or via a slash command.

---

## 2. Core Concept

### How Skill Files Work Internally

Skill Files use a **progressive loading** strategy with three stages:

```
Stage 1: DISCOVERY       → Agent reads only `name` + `description` (~100 tokens)
                            Decides: "Is this skill relevant to the current task?"
                               ↓ Yes
Stage 2: INSTRUCTIONS    → Agent loads the full SKILL.md body (<5000 tokens)
                            Gets: procedures, checklists, rules
                               ↓ If references are needed
Stage 3: RESOURCES       → Agent loads referenced files (scripts, templates, docs)
                            Gets: ./scripts/*, ./references/*, ./assets/*
```

This is deliberate — it keeps the context window lean. A project with 10 skills only costs ~1000 tokens at idle (10 × ~100 tokens for discovery), not 50,000.

### Key Components and Structure

Every skill has **two parts**: the **YAML frontmatter** (metadata) and the **Markdown body** (instructions).

**YAML Frontmatter fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | 1–64 chars, lowercase + hyphens. **Must match the folder name.** |
| `description` | Yes | Max 1024 chars. The **discovery surface** — include trigger phrases here. |
| `argument-hint` | No | Hint text shown when the user types `/skill-name` in chat. |
| `user-invocable` | No | `true` (default) — appears as a `/` slash command. |
| `disable-model-invocation` | No | `false` (default) — allows auto-triggering by the model. |

**Folder structure:**

```
.github/skills/<skill-name>/
├── SKILL.md           # Required — the skill definition
├── scripts/           # Optional — executable code the skill can run
├── references/        # Optional — docs loaded when referenced
└── assets/            # Optional — templates, boilerplate files
```

---

## 3. Creation Guide

### Step-by-Step Process

**Step 1 — Identify a repeatable workflow.**
Ask: "Do I keep giving Copilot the same multi-step instructions?" If yes, that's a skill candidate.

**Step 2 — Create the folder.**
The folder name becomes the skill's identity. It must match the `name` field exactly.

```
.github/skills/my-new-skill/
```

**Step 3 — Write the YAML frontmatter.**
This is the most critical part. The `description` determines whether the skill ever gets activated.

```yaml
---
name: my-new-skill
description: 'Generates X when the user asks for Y. Use for: creating widgets,
  building forms, scaffolding components. TRIGGER PHRASES: generate widget,
  create form, add component.'
argument-hint: 'What to generate: widget | form | component'
---
```

**Step 4 — Write the Markdown body.**
Structure it as a procedure:

1. What the skill produces (expected output)
2. Required information (what to ask the user)
3. Step-by-step procedure (the actual workflow)
4. Validation checklist (quality gates)
5. Output summary (what to report when done)

**Step 5 — Add resource files (optional).**
If your skill needs scripts, templates, or reference docs, add them as sub-folders and link with relative paths:

```markdown
Run the [setup script](./scripts/setup.sh) first.
See [API reference](./references/api-spec.md) for field definitions.
```

**Step 6 — Validate.**

- Folder name matches `name` field? ✅
- Description has keyword-rich trigger phrases? ✅
- SKILL.md body under 500 lines? ✅
- All resource paths use `./` relative notation? ✅

### Best Practices

- **Pack the description with trigger phrases.** The description is the *only* thing the agent reads during discovery. No keywords = never triggered.
- **Use the `TRIGGER PHRASES:` convention.** Explicitly listing trigger phrases at the end of the description is an effective pattern.
- **Keep SKILL.md under 500 lines.** Move detailed reference content into `./references/` files.
- **Be procedural, not theoretical.** Write step-by-step instructions, not explanations.
- **Include a "Required Information" section.** Tell the agent what to ask the user before proceeding.

### Common Mistakes

| Mistake | Why It Fails | Fix |
|---------|-------------|-----|
| Vague description: `"A helpful skill"` | Agent can't match it to any task | Include specific trigger words and use cases |
| `name: mySkill` but folder is `my-skill/` | Silent failure — skill is never found | Names must match exactly |
| Monolithic 1000-line SKILL.md | Wastes context tokens, slower loading | Split into `SKILL.md` + `./references/` |
| Unescaped colons in YAML description | YAML parse failure (silent!) | Wrap description in quotes: `description: "Use when: ..."` |
| Hardcoded absolute paths to resources | Breaks on other machines | Always use `./` relative paths |

---

## 4. Usage Guide

### How to Integrate Skill Files Into Your Project

**Option A — Automatic invocation (default behavior)**

Just create the skill. When a user types something that matches the description's keywords, Copilot automatically loads and follows the skill. No configuration needed.

Example: With the `db-migration` skill, typing *"create a migration to add a priority column to todos"* automatically triggers the skill because `"create migration"` and `"add column"` are in its description.

**Option B — Manual slash command invocation**

Type `/` in the Copilot chat, then select the skill name from the list.

```
/dev-runner backend
/api-endpoint-generation
/test-generator
```

The `argument-hint` field controls what hint text appears after the skill name.

### Invocation Control Matrix

| `user-invocable` | `disable-model-invocation` | Slash command? | Auto-triggered? |
|:-:|:-:|:-:|:-:|
| `true` (default) | `false` (default) | Yes | Yes |
| `false` | `false` | No | Yes |
| `true` | `true` | Yes | No |
| `false` | `true` | No | No |

### Typical Workflow and Lifecycle

```
1. Developer types: "generate endpoint for tags"
2. Agent scans all skills' `description` fields (~100 tokens each)
3. Agent matches "generate endpoint" → api-endpoint-generation skill
4. Agent loads full SKILL.md body
5. Agent follows the procedure:
   a. Asks for missing info (fields, validation rules, etc.)
   b. Generates code in the documented order
   c. Runs the output checklist
6. Agent reports the output summary
```

---

## 5. Importance

### Why Skill Files Matter

**1. Consistency.** Without skills, every developer on a team prompts Copilot differently, getting inconsistent output. A skill ensures the same procedure every time — same layer order, same status codes, same error handling patterns.

**2. Context efficiency.** Unlike workspace instructions (`copilot-instructions.md`) which are loaded into *every* conversation, skills load only when relevant. A project with 7 skills carries ~700 tokens at idle — not 35,000.

**3. Team knowledge encoding.** Skills capture institutional knowledge — "how we do migrations", "how we generate endpoints" — in a versionable, reviewable format that lives alongside the code.

**4. Reduced prompt engineering.** Instead of crafting a 200-word prompt each time, you type `/api-endpoint-generation` and the agent already knows the full procedure.

### Problems They Solve

| Problem | How Skills Fix It |
|---------|------------------|
| Inconsistent code generation across team members | Shared skill defines exact procedure and quality checklist |
| Copilot "forgets" project conventions mid-conversation | Skill is loaded fresh each invocation with full procedure |
| Wasted context window on always-loaded instructions | Progressive loading means idle skills cost ~100 tokens each |
| Repeating the same complex prompt in every conversation | Encode once, invoke with a keyword or slash command |
| New developers don't know project workflows | Skills serve as executable documentation |

---

## 6. Use Cases

### Real-World Examples

| Skill | Real-World Scenario |
|-------|-------------------|
| `api-endpoint-generation` | A developer says "add a tags endpoint." The skill generates all 3 layers (Route → Service → Repository) with DI wiring, schemas, and migration guidance in the correct order. |
| `db-migration` | A developer changes a SQLAlchemy model. The skill catches data-loss risks, ensures `downgrade()` is implemented, checks SQL Server compatibility, and guides the full Alembic workflow. |
| `dev-runner` | A new team member says "start the app." The skill knows the exact commands, ports, pre-flight checks, and health verification for both backend and frontend. |
| `test-generator` | After creating a new service, a developer says "write tests for this." The skill produces AAA-pattern pytest tests with proper mocking, naming conventions, and coverage targets. |
| `security-review` | Before a release, a developer says "security audit." The skill performs an OWASP Top 10 mapped review of both backend and frontend, reporting PASS/WARN/FAIL per category. |
| `performance-review` | A developer suspects slow queries. The skill checks for N+1 queries, missing indexes, unnecessary re-renders, and network inefficiencies. |
| `test-runner` | A developer says "run all tests." The skill detects context, runs the correct suite, and reports results with suggested fixes. |

### Industry Scenarios

- **Design system team:** A `component-scaffold` skill that generates a React component with Storybook stories, unit tests, and accessibility props in the team's exact pattern.
- **DevOps team:** A `terraform-module` skill that scaffolds Terraform modules with correct provider config, state backend, and variable validation.
- **Data engineering:** A `pipeline-generator` skill that creates Airflow DAGs following the team's naming, retry, and alerting conventions.

---

## 7. Demo Project

Let's build a complete demo — a skill that generates React components following a team convention.

### Architecture

```
my-project/
├── .github/
│   └── skills/
│       └── component-generator/       ← Our new skill
│           └── SKILL.md
├── src/
│   └── components/                    ← Where generated components go
└── package.json
```

### The Skill File

**File:** `.github/skills/component-generator/SKILL.md`

```markdown
---
name: component-generator
description: 'Generates React functional components with TypeScript props, CSS Module,
  and a co-located test file. Use for: creating components, scaffolding UI, adding
  new component. TRIGGER PHRASES: generate component, create component, add component,
  scaffold component.'
argument-hint: 'Component name, e.g., UserCard'
---

# Component Generator

## What This Skill Produces
A complete React component set: component file, CSS Module, types, and test file.

## Required Information
Before generating, confirm:
- Component name (PascalCase): e.g., `UserCard`
- Props (name + type): e.g., `title: string`, `isActive: boolean`
- Whether it has children (`children?: React.ReactNode`)

## Procedure

### 1. Create the Component File (`src/components/<Name>.tsx`)
- Functional arrow component (no `React.FC`)
- Import props interface from the types file
- Import CSS module

### 2. Create the Props Type (`src/types/<name>.ts`)
- Export an interface `<Name>Props` with all specified props

### 3. Create the CSS Module (`src/components/<Name>.module.css`)
- Add a `.container` class with basic layout styles

### 4. Create the Test File (`src/components/__tests__/<Name>.test.tsx`)
- Test: renders with valid props
- Test: conditional rendering for boolean props
- Test: handles missing optional props

## Output Summary
After generating, report:
1. Files created (4 files)
2. Props interface
3. Reminder to export from barrel file if one exists
```

### Sample Generated Output

When a developer types **"create a UserCard component with title and isActive props"**, the skill generates these files:

**`src/types/userCard.ts`**

```typescript
export interface UserCardProps {
  title: string;
  isActive: boolean;
}
```

**`src/components/UserCard.tsx`**

```tsx
import styles from './UserCard.module.css';
import { UserCardProps } from '../types/userCard';

const UserCard = ({ title, isActive }: UserCardProps) => {
  return (
    <div className={styles.container}>
      <h2>{title}</h2>
      {isActive && <span className={styles.badge}>Active</span>}
    </div>
  );
};

export { UserCard };
```

**`src/components/UserCard.module.css`**

```css
.container {
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.badge {
  color: green;
  font-weight: bold;
}
```

**`src/components/__tests__/UserCard.test.tsx`**

```tsx
import { render, screen } from '@testing-library/react';
import { UserCard } from '../UserCard';

describe('UserCard', () => {
  it('renders title correctly', () => {
    render(<UserCard title="Test" isActive={false} />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('shows active badge when isActive is true', () => {
    render(<UserCard title="Test" isActive={true} />);
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('hides active badge when isActive is false', () => {
    render(<UserCard title="Test" isActive={false} />);
    expect(screen.queryByText('Active')).not.toBeInTheDocument();
  });
});
```

### Flow Diagram

```
User: "create a UserCard component"
         │
         ▼
┌─────────────────────┐
│  Discovery Phase    │  Agent reads name + description
│  (~100 tokens)      │  Matches "create component"
└────────┬────────────┘
         ▼
┌─────────────────────┐
│  Load SKILL.md      │  Full procedure loaded
│  (~2000 tokens)     │  into context
└────────┬────────────┘
         ▼
┌─────────────────────┐
│  Execute Procedure  │
│  Step 1: Component  │──→ src/components/UserCard.tsx
│  Step 2: Types      │──→ src/types/userCard.ts
│  Step 3: CSS Module │──→ src/components/UserCard.module.css
│  Step 4: Test File  │──→ src/components/__tests__/UserCard.test.tsx
└────────┬────────────┘
         ▼
┌─────────────────────┐
│  Output Summary     │  "Created 4 files for UserCard"
└─────────────────────┘
```

---

## 8. Project Ideas

### Idea 1: `api-crud-generator` Skill (Beginner)

**Goal:** Generate Express.js CRUD routes + Prisma model for any resource.

- User says: "generate CRUD for Product"
- Skill creates: Prisma schema addition, route file, controller, and validation middleware
- **What you'll learn:** Frontmatter design, multi-file generation procedures, required-info gathering

### Idea 2: `readme-generator` Skill (Beginner)

**Goal:** Generate a standardized `README.md` for any project by scanning the codebase.

- User says: "generate readme"
- Skill procedure: scan `package.json`/`pyproject.toml` → detect tech stack → generate sections (Install, Usage, API, Contributing)
- **What you'll learn:** Skills that reference codebase context, conditional logic in procedures

### Idea 3: `docker-setup` Skill (Intermediate)

**Goal:** Generate `Dockerfile` + `docker-compose.yml` matching the project's tech stack.

- User says: "add Docker support"
- Skill procedure: detect runtime (Node/Python/Go) → pick base image → generate multi-stage Dockerfile → generate compose file with DB service
- Includes a `./references/base-images.md` file with recommended images per runtime
- **What you'll learn:** Skills with bundled reference files, progressive resource loading

---

## 9. Conclusion

### Key Takeaways

1. **A Skill File is a `SKILL.md` inside a named folder** at `.github/skills/<name>/`. The folder name must match the `name` frontmatter field.

2. **The `description` is everything.** It's the only thing the agent reads at discovery time. Pack it with specific trigger phrases and use-case keywords.

3. **Progressive loading keeps things fast.** Discovery (~100 tokens) → Instructions (<5000 tokens) → Resources (on-demand). Idle skills are nearly free.

4. **Write procedures, not theory.** Skills should read like a step-by-step playbook — "do this, then this, then validate with this checklist."

5. **Skills complement other primitives.** Use workspace instructions (`copilot-instructions.md`) for always-on rules, file instructions (`.instructions.md`) for file-scoped rules, and skills for on-demand workflows.

6. **Start simple.** Your first skill can be a single `SKILL.md` with no resource files — just frontmatter + a procedure. Add `scripts/`, `references/`, and `assets/` folders as complexity grows.

### Comparison with Other Primitives

| Primitive | Scope | Loading | Best For |
|-----------|-------|---------|----------|
| `copilot-instructions.md` | Always-on, every conversation | Automatic | Project-wide rules and conventions |
| `*.instructions.md` | File-pattern scoped via `applyTo` | When matching files are active | File-type-specific rules |
| `SKILL.md` | On-demand, keyword-triggered | Only when relevant | Repeatable multi-step workflows |
| `*.prompt.md` | On-demand, user-invoked | Only when selected | Single focused tasks with inputs |
| `*.agent.md` | On-demand, user-invoked | Only when selected | Context-isolated subagent workflows |
