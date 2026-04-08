import { CategoryManager } from '@/components/CategoryManager'
import { TodoForm } from '@/components/TodoForm'
import { TodoList } from '@/components/TodoList'
import { useCreateTodo } from '@/hooks/useTodos'
import { useTodos } from '@/hooks/useTodos'

const TodoPage = () => {
  const createTodo = useCreateTodo()
  const { data: todos } = useTodos()

  const total = todos?.length ?? 0
  const completed = todos?.filter((t) => t.isCompleted).length ?? 0
  const progress = total > 0 ? Math.round((completed / total) * 100) : 0

  return (
    <div className="relative mx-auto max-w-2xl px-4 py-12 animate-fade-in">
      {/* Header */}
      <div className="mb-10 text-center">
        <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-primary-100/80 px-4 py-1.5 text-xs font-semibold tracking-wide text-primary-700 uppercase backdrop-blur-sm">
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
          </svg>
          Organize your day
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">
          My Todos
        </h1>
        {total > 0 && (
          <div className="mt-4 flex items-center justify-center gap-3">
            <div className="h-2 w-40 overflow-hidden rounded-full bg-slate-200">
              <div
                className="h-full rounded-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
            <span className="text-xs font-medium text-slate-500">
              {completed}/{total} done
            </span>
          </div>
        )}
      </div>

      <div className="space-y-5">
        <CategoryManager />
        <TodoForm
          onSubmit={(data) => createTodo.mutate(data)}
          isLoading={createTodo.isPending}
        />
        <section aria-label="Todo list">
          <TodoList />
        </section>
      </div>
    </div>
  )
}

export default TodoPage
