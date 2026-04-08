import { api } from './api'
import type { Category, CategoryCreate, CategoryUpdate } from '@/types'

export const categoryService = {
  getAll: async (): Promise<Category[]> => {
    const { data } = await api.get<Category[]>('/categories')
    return data
  },

  getById: async (id: number): Promise<Category> => {
    const { data } = await api.get<Category>(`/categories/${id}`)
    return data
  },

  create: async (payload: CategoryCreate): Promise<Category> => {
    const { data } = await api.post<Category>('/categories', payload)
    return data
  },

  update: async (id: number, payload: CategoryUpdate): Promise<Category> => {
    const { data } = await api.put<Category>(`/categories/${id}`, payload)
    return data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/categories/${id}`)
  },
}
