/**
 * TodosPage.tsx
 *
 * Top-level page for the Todo list view.
 * Composes TodoForm (create) and a list of TodoItem rows.
 *
 * Handles three loading states: loading, error, and success.
 * All server state comes from useTodos — no local state for API data.
 */

import { TodoForm } from "../components/TodoForm";
import { TodoItem } from "../components/TodoItem";
import { useTodos } from "../hooks/useTodos";

export function TodosPage() {
  const { data: todos, isLoading, isError } = useTodos();

  return (
    <div style={{ maxWidth: "640px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1.5rem" }}>My Todos</h1>

      {/* Create form always visible at the top */}
      <TodoForm />

      {/* Loading state */}
      {isLoading && <p style={{ color: "#666" }}>Loading todos…</p>}

      {/* Error state */}
      {isError && (
        <p style={{ color: "red" }}>
          Failed to load todos. Make sure the API is running.
        </p>
      )}

      {/* Empty state */}
      {!isLoading && !isError && todos?.length === 0 && (
        <p style={{ color: "#888" }}>No todos yet. Add one above!</p>
      )}

      {/* Todo list */}
      {todos && todos.length > 0 && (
        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          {todos.map((todo) => (
            <TodoItem key={todo.id} todo={todo} />
          ))}
        </ul>
      )}
    </div>
  );
}
