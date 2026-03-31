/**
 * todoService.ts
 *
 * Axios-based API client for the Todo domain.
 * All functions talk to the FastAPI /api/todos endpoints.
 *
 * Rules:
 *  - This file is the ONLY place that knows the todo API URL shape.
 *  - Functions return typed data; callers never touch raw Axios responses.
 *  - No React or React Query here — this is plain async/await.
 */

import { api } from "./api";
import type { CreateTodoRequest, Todo, UpdateTodoRequest } from "../types";

/** Fetch all todos (newest first). */
async function getAll(): Promise<Todo[]> {
  const response = await api.get<Todo[]>("/api/todos/");
  return response.data;
}

/** Fetch a single Todo by its id. Throws on 404. */
async function getById(id: number): Promise<Todo> {
  const response = await api.get<Todo>(`/api/todos/${id}`);
  return response.data;
}

/** Create a new Todo. Returns the created resource (201). */
async function create(data: CreateTodoRequest): Promise<Todo> {
  const response = await api.post<Todo>("/api/todos/", data);
  return response.data;
}

/**
 * Partially update an existing Todo.
 * Only include fields you want to change — omitted fields are untouched.
 */
async function update(id: number, data: UpdateTodoRequest): Promise<Todo> {
  const response = await api.patch<Todo>(`/api/todos/${id}`, data);
  return response.data;
}

/** Delete a Todo by id. Returns void (204). */
async function remove(id: number): Promise<void> {
  await api.delete(`/api/todos/${id}`);
}

export const todoService = { getAll, getById, create, update, remove };
