import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { categoryService } from '@/services/categoryService'
import type { CategoryCreate, CategoryUpdate } from '@/types'

export const useCategories = () =>
  useQuery({
    queryKey: ['categories'],
    queryFn: categoryService.getAll,
  })

export const useCategory = (id: number) =>
  useQuery({
    queryKey: ['categories', id],
    queryFn: () => categoryService.getById(id),
    enabled: !!id,
  })

export const useCreateCategory = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CategoryCreate) => categoryService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
  })
}

export const useUpdateCategory = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CategoryUpdate }) =>
      categoryService.update(id, data),
    onSuccess: (_data, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
      queryClient.invalidateQueries({ queryKey: ['categories', id] })
    },
  })
}

export const useDeleteCategory = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => categoryService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}
