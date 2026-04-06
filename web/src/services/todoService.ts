import { api } from './api'
import type { Todo, TodoCreate, TodoUpdate } from '@/types'

export const todoService = {
  getAll: async (): Promise<Todo[]> => {
    const { data } = await api.get<Todo[]>('/todos')
    return data
  },

  getById: async (id: number): Promise<Todo> => {
    const { data } = await api.get<Todo>(`/todos/${id}`)
    return data
  },

  create: async (payload: TodoCreate): Promise<Todo> => {
    const { data } = await api.post<Todo>('/todos', payload)
    return data
  },

  update: async (id: number, payload: TodoUpdate): Promise<Todo> => {
    const { data } = await api.put<Todo>(`/todos/${id}`, payload)
    return data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/todos/${id}`)
  },
}
