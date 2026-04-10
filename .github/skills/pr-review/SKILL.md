---
name: pr-review
description: "Combined skill for pre-merge pull request review. Runs all tests, performs a security audit, and checks for performance issues — all in one pass. Delegates to test-runner, security-review, and performance-review skills in sequence. TRIGGER PHRASES: pr review, pull request review, code review, review before merge, pre-merge check, review this pr, full review, review my changes."
argument-hint: "Optionally specify: backend | frontend | all (default: auto-detect from changed files)"
user-invocable: true
disable-model-invocation: false
---

# PR Review (Combined Skill)

## What This Skill Produces
A single, unified pre-merge report that combines **three skills** in sequence:

1. **Test Runner** — verify all tests pass
2. **Security Review** — OWASP Top 10 audit
3. **Performance Review** — bottleneck & efficiency check

The final output is a **merge verdict**: ✅ Ready / ⚠️ Conditional / ❌ Blocked.

---

## Execution Order

### Phase 1 — Scope Detection

Determine which parts of the codebase were changed:

1. Run `git diff --name-only main...HEAD` (or `git diff --name-only HEAD~1` if no PR branch).
2. Classify changed files:
   - Files in `api/` → backend scope
   - Files in `web/` → frontend scope
   - Both → full-stack scope
3. If no git diff available, ask the user: _"Which area should I review: backend, frontend, or both?"_

---

### Phase 2 — Test Runner (Skill: `test-runner`)

**Goal: All tests must pass before reviewing code quality.**

- **Backend** (if in scope): `cd api; pytest -v --tb=short`
- **Frontend** (if in scope): `cd web; npm run test`

Report the test summary table (total / passed / failed / skipped / duration).

**Gate rule:**
- If any test **fails** → mark Phase 2 as ❌ BLOCKED. Still proceed to Phases 3-4 but flag the merge verdict as blocked.
- If all tests pass → mark Phase 2 as ✅ PASS.

---

### Phase 3 — Security Review (Skill: `security-review`)

**Goal: No critical or high-severity vulnerabilities.**

Run the full OWASP Top 10 audit against **changed files only** (not the entire codebase), scanning:

- **Backend**: injection, secrets in code, CORS config, error leak, input validation, bare excepts
- **Frontend**: XSS, dangerouslySetInnerHTML, exposed secrets in VITE_* vars, CSRF on mutations

Report each finding as ✅ PASS / ⚠️ WARN / ❌ FAIL with severity.

**Gate rule:**
- Any **Critical** or **High** finding → mark Phase 3 as ❌ BLOCKED.
- Only **Medium** or **Low** findings → mark Phase 3 as ⚠️ WARN.
- No findings → mark Phase 3 as ✅ PASS.

---

### Phase 4 — Performance Review (Skill: `performance-review`)

**Goal: No high-severity performance regressions.**

Review **changed files only** for:

- **Backend**: N+1 queries, missing eager loads, sync calls in async, missing pagination
- **Frontend**: unnecessary re-renders, missing staleTime, waterfall requests, missing memo/callback

Report each finding with severity and expected impact.

**Gate rule:**
- Any **High** finding → mark Phase 4 as ⚠️ WARN (performance issues rarely block merge, but must be tracked).
- Only **Medium** or **Low** → mark Phase 4 as ✅ PASS.

---

## Output Format

### Per-Phase Reports

Each phase outputs its own table following the format defined in its respective skill.

### Unified Summary

```
╔══════════════════════════════════════════════════════════╗
║                   PR REVIEW SUMMARY                      ║
╠══════════════════════════════════════════════════════════╣
║  Phase 1 — Scope        : backend | frontend | both     ║
║  Phase 2 — Tests        : ✅ PASS | ❌ BLOCKED           ║
║  Phase 3 — Security     : ✅ PASS | ⚠️ WARN | ❌ BLOCKED ║
║  Phase 4 — Performance  : ✅ PASS | ⚠️ WARN              ║
╠══════════════════════════════════════════════════════════╣
║  MERGE VERDICT          : ✅ Ready | ⚠️ Conditional | ❌  ║
╚══════════════════════════════════════════════════════════╝
```

### Merge Verdict Rules

| Verdict | Condition |
|---------|-----------|
| ✅ **Ready to merge** | All phases ✅ PASS |
| ⚠️ **Conditional merge** | All phases pass but with ⚠️ WARNs — list items to address post-merge |
| ❌ **Blocked** | Any phase is ❌ BLOCKED — list blocking items that must be fixed first |

### Action Items

After the summary, list:

1. **Must fix before merge** — blocking issues (failed tests, critical security findings)
2. **Should fix before merge** — high-severity warnings
3. **Track for later** — medium/low items to address in follow-up commits

---

## Rules

- Always run tests FIRST — if the code doesn't even pass tests, that's the priority.
- Scope reviews to **changed files** when possible — avoid reviewing the entire codebase on every PR.
- Never auto-fix code during a review — only report findings and suggest fixes.
- If a phase skill reports a finding, include the file and line reference.
- Report each phase even if a previous phase is blocked — the developer benefits from seeing all issues at once.
