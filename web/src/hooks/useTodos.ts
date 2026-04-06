import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { todoService } from '@/services/todoService'
import type { TodoCreate, TodoUpdate } from '@/types'

export const useTodos = () =>
  useQuery({
    queryKey: ['todos'],
    queryFn: todoService.getAll,
  })

export const useTodo = (id: number) =>
  useQuery({
    queryKey: ['todos', id],
    queryFn: () => todoService.getById(id),
    enabled: !!id,
  })

export const useCreateTodo = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: TodoCreate) => todoService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}

export const useUpdateTodo = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TodoUpdate }) =>
      todoService.update(id, data),
    onSuccess: (_data, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
      queryClient.invalidateQueries({ queryKey: ['todos', id] })
    },
  })
}

export const useDeleteTodo = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => todoService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}
