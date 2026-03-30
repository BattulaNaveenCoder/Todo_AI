---
description: "Run a code review checklist before creating a PR"
---

Review all changes on the current branch vs main. Check:

1. **Architecture compliance** — Routes have no business logic? Services have no SQL? Repositories have no HTTP?
2. **Type safety** — All functions have type hints (Python) or strict types (TypeScript)?
3. **Error handling** — Proper HTTP status codes? No bare except clauses? Frontend error boundaries?
4. **Security** — No secrets in code? No SQL injection? Input validated via Pydantic/Zod?
5. **Async correctness** — All DB operations awaited? No sync calls in async context?
6. **Tests** — Do tests exist for new code? Do they cover happy path + edge cases?
7. **Documentation** — Docstrings on public functions? Complex logic commented?

Output a markdown checklist with ✅ / ❌ for each item and explain any failures.
