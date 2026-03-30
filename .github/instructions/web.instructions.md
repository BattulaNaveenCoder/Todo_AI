---
applyTo: "web/src/**/*.{ts,tsx}"
---

# React & TypeScript Instructions

- TypeScript strict mode — no `any` types, no type assertions unless justified
- Functional components only — no class components
- Use React Query (TanStack) for all server state — no useState for API data
- Custom hooks in /hooks/ folder — one hook file per domain (useTodos.ts, useCategories.ts)
- API service functions in /services/ — one file per domain (todoService.ts)
- All types/interfaces in /types/ — export from index.ts barrel file
- Use named exports, not default exports
- Error boundaries for top-level pages
- Axios instance with baseURL configured in /services/api.ts
