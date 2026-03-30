/** Core Todo entity returned from the API */
export interface Todo {
  id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

/** Payload for creating a new Todo */
export interface CreateTodoRequest {
  title: string;
  description?: string | null;
}

/** Payload for updating an existing Todo */
export interface UpdateTodoRequest {
  title?: string;
  description?: string | null;
  is_completed?: boolean;
}

// Types will be expanded in Phase 1 and Phase 3 (categories)
