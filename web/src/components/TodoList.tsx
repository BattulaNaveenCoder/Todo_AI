import { TodoItem } from './TodoItem'
import { useTodos, useUpdateTodo, useDeleteTodo } from '@/hooks/useTodos'

export const TodoList = () => {
  const { data: todos, isLoading, isError, error } = useTodos()
  const updateTodo = useUpdateTodo()
  const deleteTodo = useDeleteTodo()

  if (isLoading) {
    return (
      <div role="status" className="flex flex-col items-center gap-3 py-16 animate-fade-in">
        <svg className="h-8 w-8 animate-spin text-primary-400" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <span className="text-sm text-slate-400">Loading todos…</span>
      </div>
    )
  }

  if (isError) {
    return (
      <div role="alert" className="rounded-2xl border border-red-200 bg-red-50/80 px-5 py-4 text-sm text-red-600 backdrop-blur-xl">
        <div className="flex items-center gap-2">
          <svg className="h-5 w-5 shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
          </svg>
          Error: {(error as Error).message}
        </div>
      </div>
    )
  }

  if (!todos?.length) {
    return (
      <div className="flex flex-col items-center gap-3 py-16 animate-fade-in">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100">
          <svg className="h-8 w-8 text-slate-300" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25Z" />
          </svg>
        </div>
        <div className="text-center">
          <p className="text-sm font-medium text-slate-500">No todos yet</p>
          <p className="mt-0.5 text-xs text-slate-400">Create your first task above!</p>
        </div>
      </div>
    )
  }

  const handleToggle = (id: number) => {
    const todo = todos.find((t) => t.id === id)
    if (!todo) return
    updateTodo.mutate({ id, data: { isCompleted: !todo.isCompleted } })
  }

  const handleDelete = (id: number) => {
    deleteTodo.mutate(id)
  }

  return (
    <ul className="space-y-2.5">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={handleToggle}
          onDelete={handleDelete}
        />
      ))}
    </ul>
  )
}
