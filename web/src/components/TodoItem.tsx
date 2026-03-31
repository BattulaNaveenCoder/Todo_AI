/**
 * TodoItem.tsx
 *
 * Renders a single Todo row with:
 *  - Checkbox to toggle completion (useUpdateTodo)
 *  - Title and optional description
 *  - Delete button (useDeleteTodo)
 *
 * Props:
 *  todo — the Todo object to display
 */

import { useDeleteTodo, useUpdateTodo } from "../hooks/useTodos";
import type { Todo } from "../types";

interface TodoItemProps {
  todo: Todo;
}

export function TodoItem({ todo }: TodoItemProps) {
  const updateTodo = useUpdateTodo();
  const deleteTodo = useDeleteTodo();

  /** Toggle the is_completed flag on the server. */
  function handleToggle() {
    updateTodo.mutate({
      id: todo.id,
      data: { is_completed: !todo.is_completed },
    });
  }

  /** Remove this todo from the server. */
  function handleDelete() {
    deleteTodo.mutate(todo.id);
  }

  // Visual styling: strike-through completed items
  const titleStyle: React.CSSProperties = {
    textDecoration: todo.is_completed ? "line-through" : "none",
    color: todo.is_completed ? "#888" : "inherit",
    fontWeight: 500,
  };

  return (
    <li
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: "0.75rem",
        padding: "0.75rem 0",
        borderBottom: "1px solid #eee",
      }}
    >
      {/* Completion toggle checkbox */}
      <input
        type="checkbox"
        checked={todo.is_completed}
        onChange={handleToggle}
        disabled={updateTodo.isPending}
        style={{ marginTop: "0.2rem", cursor: "pointer" }}
        aria-label={`Mark "${todo.title}" as ${todo.is_completed ? "incomplete" : "complete"}`}
      />

      {/* Todo content */}
      <div style={{ flex: 1 }}>
        <p style={{ margin: 0, ...titleStyle }}>{todo.title}</p>
        {todo.description && (
          <p
            style={{
              margin: "0.25rem 0 0",
              fontSize: "0.875rem",
              color: "#555",
            }}
          >
            {todo.description}
          </p>
        )}
      </div>

      {/* Delete button */}
      <button
        onClick={handleDelete}
        disabled={deleteTodo.isPending}
        aria-label={`Delete "${todo.title}"`}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          color: "#c00",
          fontSize: "1rem",
          padding: "0 0.25rem",
        }}
      >
        ✕
      </button>
    </li>
  );
}
