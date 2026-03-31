/**
 * useTodos.ts
 *
 * React Query hooks for the Todo domain.
 * Components access all server state through these hooks — never via
 * direct Axios calls.
 *
 * Hooks exported:
 *  useTodos        — fetch the full list (useQuery)
 *  useCreateTodo   — create mutation, auto-invalidates list
 *  useUpdateTodo   — patch mutation, auto-invalidates list
 *  useDeleteTodo   — delete mutation, auto-invalidates list
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { todoService } from "../services/todoService";
import type { CreateTodoRequest, UpdateTodoRequest } from "../types";

/** Stable query key for the todo list.
 *  Using `as const` gives TypeScript a tuple type instead of string[]. */
const TODOS_QUERY_KEY = ["todos"] as const;

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

/** Fetch all todos. Refetches automatically when stale (30s via QueryClient). */
export function useTodos() {
  return useQuery({
    queryKey: TODOS_QUERY_KEY,
    queryFn: todoService.getAll,
  });
}

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

/** Create a new Todo.
 *  On success the todo list query is invalidated so the UI refreshes. */
export function useCreateTodo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTodoRequest) => todoService.create(data),
    onSuccess: () => {
      // Invalidate the list so it refetches from the server
      queryClient.invalidateQueries({ queryKey: TODOS_QUERY_KEY });
    },
  });
}

/** Partially update an existing Todo.
 *  Accepts { id, data } so the caller has a single argument object. */
export function useUpdateTodo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateTodoRequest }) =>
      todoService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TODOS_QUERY_KEY });
    },
  });
}

/** Delete a Todo by id. */
export function useDeleteTodo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => todoService.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TODOS_QUERY_KEY });
    },
  });
}
