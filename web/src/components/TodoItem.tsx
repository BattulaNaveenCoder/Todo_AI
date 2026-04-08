import { CategoryBadge } from './CategoryBadge'
import type { Todo } from '@/types'

interface TodoItemProps {
  todo: Todo
  onToggle: (id: number) => void
  onDelete: (id: number) => void
}

export const TodoItem = ({ todo, onToggle, onDelete }: TodoItemProps) => {
  return (
    <li className="group flex items-start gap-3.5 rounded-2xl border border-white/60 bg-white/70 px-4 py-4 shadow-md shadow-slate-200/40 backdrop-blur-xl transition-all duration-200 animate-slide-up hover:shadow-lg hover:shadow-slate-200/60 hover:-translate-y-0.5">
      {/* Custom checkbox */}
      <button
        type="button"
        onClick={() => onToggle(todo.id)}
        className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md border-2 transition-all duration-200 ${
          todo.isCompleted
            ? 'border-primary-500 bg-gradient-to-br from-primary-500 to-accent-500 shadow-sm shadow-primary-500/30'
            : 'border-slate-300 bg-white hover:border-primary-400 hover:shadow-sm hover:shadow-primary-200/50'
        }`}
        role="checkbox"
        aria-checked={todo.isCompleted}
        aria-label={`Mark "${todo.title}" as ${todo.isCompleted ? 'incomplete' : 'complete'}`}
      >
        {todo.isCompleted && (
          <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
          </svg>
        )}
      </button>

      {/* Content */}
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span
            className={`text-sm font-medium transition-all duration-300 ${
              todo.isCompleted
                ? 'text-slate-400 line-through decoration-slate-300'
                : 'text-slate-800'
            }`}
          >
            {todo.title}
          </span>
          <CategoryBadge categoryName={todo.categoryName} />
        </div>
        {todo.description && (
          <p
            className={`mt-1 text-xs leading-relaxed transition-all duration-300 ${
              todo.isCompleted ? 'text-slate-300' : 'text-slate-500'
            }`}
          >
            {todo.description}
          </p>
        )}
      </div>

      {/* Delete button */}
      <button
        onClick={() => onDelete(todo.id)}
        className="shrink-0 rounded-lg p-1.5 text-slate-300 opacity-0 transition-all duration-200 hover:bg-red-50 hover:text-red-500 group-hover:opacity-100"
        aria-label={`Delete "${todo.title}"`}
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
        </svg>
      </button>
    </li>
  )
}
