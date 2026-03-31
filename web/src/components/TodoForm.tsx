/**
 * TodoForm.tsx
 *
 * Controlled form for creating a new Todo.
 * Calls useCreateTodo and resets itself on success.
 *
 * Props:
 *  (none — self-contained, uses internal mutation hook)
 */

import { type FormEvent, useState } from "react";

import { useCreateTodo } from "../hooks/useTodos";

export function TodoForm() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const createTodo = useCreateTodo();

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const trimmedTitle = title.trim();
    if (!trimmedTitle) return; // guard: title is required

    createTodo.mutate(
      { title: trimmedTitle, description: description.trim() || null },
      {
        onSuccess: () => {
          // Reset fields after successful creation
          setTitle("");
          setDescription("");
        },
      },
    );
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "1.5rem" }}>
      <h2 style={{ marginBottom: "0.75rem" }}>Add Todo</h2>

      {/* Title field — required */}
      <div style={{ marginBottom: "0.5rem" }}>
        <input
          type="text"
          placeholder="Title *"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={255}
          required
          style={{ width: "100%", padding: "0.4rem", boxSizing: "border-box" }}
        />
      </div>

      {/* Description field — optional */}
      <div style={{ marginBottom: "0.5rem" }}>
        <textarea
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={2}
          style={{ width: "100%", padding: "0.4rem", boxSizing: "border-box" }}
        />
      </div>

      <button type="submit" disabled={createTodo.isPending}>
        {createTodo.isPending ? "Saving…" : "Add Todo"}
      </button>

      {/* Inline error feedback */}
      {createTodo.isError && (
        <p style={{ color: "red", marginTop: "0.5rem" }}>
          Failed to create todo. Please try again.
        </p>
      )}
    </form>
  );
}
