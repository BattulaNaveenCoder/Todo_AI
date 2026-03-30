---
description: "Generate a conventional commit message from staged changes"
---

Analyze the currently staged git changes (`git diff --cached`) and generate a commit message following Conventional Commits:

Format: <type>(<scope>): <short summary>

Types: feat, fix, chore, docs, test, refactor
Scope: api, web, config, db, or the specific module name
Summary: imperative mood, lowercase, no period, max 72 chars

If multiple changes span concerns, use the dominant type.
Add a body paragraph only if the change is non-trivial.
