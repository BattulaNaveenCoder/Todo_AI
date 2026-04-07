import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import { TodoList } from '../TodoList'
import type { Todo } from '@/types'

vi.mock('@/hooks/useTodos', () => ({
  useTodos: vi.fn(),
  useUpdateTodo: vi.fn(() => ({ mutate: vi.fn() })),
  useDeleteTodo: vi.fn(() => ({ mutate: vi.fn() })),
}))

import { useTodos, useUpdateTodo, useDeleteTodo } from '@/hooks/useTodos'

const mockUseTodos = vi.mocked(useTodos)
const mockUseUpdateTodo = vi.mocked(useUpdateTodo)
const mockUseDeleteTodo = vi.mocked(useDeleteTodo)

const makeTodo = (overrides: Partial<Todo> = {}): Todo => ({
  id: 1,
  title: 'Test todo',
  description: null,
  isCompleted: false,
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T00:00:00Z',
  ...overrides,
})

beforeEach(() => {
  mockUseUpdateTodo.mockReturnValue({ mutate: vi.fn() } as unknown as ReturnType<typeof useUpdateTodo>)
  mockUseDeleteTodo.mockReturnValue({ mutate: vi.fn() } as unknown as ReturnType<typeof useDeleteTodo>)
})

describe('TodoList', () => {
  it('renders a loading indicator with role "status" when isLoading is true', () => {
    mockUseTodos.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    } as unknown as ReturnType<typeof useTodos>)

    render(<TodoList />)

    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('renders an error alert when isError is true', () => {
    mockUseTodos.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('Network error'),
    } as unknown as ReturnType<typeof useTodos>)

    render(<TodoList />)

    expect(screen.getByRole('alert')).toBeInTheDocument()
  })

  it('renders an empty-state message when the todo list is empty', () => {
    mockUseTodos.mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
      error: null,
    } as unknown as ReturnType<typeof useTodos>)

    render(<TodoList />)

    expect(screen.getByText(/no todos yet/i)).toBeInTheDocument()
  })

  it('renders all todo items when data is populated', () => {
    const todos = [
      makeTodo({ id: 1, title: 'First task' }),
      makeTodo({ id: 2, title: 'Second task' }),
    ]
    mockUseTodos.mockReturnValue({
      data: todos,
      isLoading: false,
      isError: false,
      error: null,
    } as unknown as ReturnType<typeof useTodos>)

    render(<TodoList />)

    expect(screen.getByText('First task')).toBeInTheDocument()
    expect(screen.getByText('Second task')).toBeInTheDocument()
  })

  it('calls deleteTodo mutate with the correct id when delete is triggered', async () => {
    const user = userEvent.setup()
    const mutateMock = vi.fn()
    mockUseDeleteTodo.mockReturnValue({ mutate: mutateMock } as unknown as ReturnType<typeof useDeleteTodo>)
    const todos = [makeTodo({ id: 5, title: 'Delete me' })]
    mockUseTodos.mockReturnValue({
      data: todos,
      isLoading: false,
      isError: false,
      error: null,
    } as unknown as ReturnType<typeof useTodos>)

    render(<TodoList />)
    await user.click(screen.getByRole('button', { name: /delete/i }))

    expect(mutateMock).toHaveBeenCalledTimes(1)
    expect(mutateMock).toHaveBeenCalledWith(5)
  })

  it('calls updateTodo mutate to toggle completion when checkbox is clicked', async () => {
    const user = userEvent.setup()
    const mutateMock = vi.fn()
    mockUseUpdateTodo.mockReturnValue({ mutate: mutateMock } as unknown as ReturnType<typeof useUpdateTodo>)
    const todos = [makeTodo({ id: 3, title: 'Toggle me', isCompleted: false })]
    mockUseTodos.mockReturnValue({
      data: todos,
      isLoading: false,
      isError: false,
      error: null,
    } as unknown as ReturnType<typeof useTodos>)

    render(<TodoList />)
    await user.click(screen.getByRole('checkbox'))

    expect(mutateMock).toHaveBeenCalledTimes(1)
    expect(mutateMock).toHaveBeenCalledWith({ id: 3, data: { isCompleted: true } })
  })
})
