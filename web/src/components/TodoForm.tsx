import { useState } from 'react'
import { CategorySelect } from './CategorySelect'
import type { TodoCreate } from '@/types'

interface TodoFormProps {
  onSubmit: (data: TodoCreate) => void
  isLoading: boolean
}

export const TodoForm = ({ onSubmit, isLoading }: TodoFormProps) => {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [categoryId, setCategoryId] = useState<number | undefined>(undefined)
  const [titleError, setTitleError] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) {
      setTitleError('Title is required.')
      return
    }
    setTitleError('')
    onSubmit({
      title: title.trim(),
      description: description.trim() || undefined,
      categoryId,
    })
    setTitle('')
    setDescription('')
    setCategoryId(undefined)
  }

  return (
    <form
      className="rounded-2xl border border-white/60 bg-white/70 p-5 shadow-lg shadow-slate-200/50 backdrop-blur-xl space-y-4 animate-slide-up"
      onSubmit={handleSubmit}
      noValidate
    >
      <div className="flex items-center gap-2.5 mb-1">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-accent-500 to-primary-600 shadow-md shadow-accent-500/25">
          <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
        </div>
        <span className="text-sm font-semibold text-slate-800">New Todo</span>
      </div>

      <div className="flex flex-col gap-1.5">
        <label htmlFor="todo-title" className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
          Title
        </label>
        <input
          id="todo-title"
          className="rounded-xl border border-slate-200 bg-slate-50/80 px-3.5 py-2.5 text-sm font-medium outline-none transition-all placeholder:text-slate-400 focus:border-primary-400 focus:bg-white focus:ring-4 focus:ring-primary-500/10"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs to be done?"
          maxLength={255}
          aria-describedby={titleError ? 'title-error' : undefined}
        />
        {titleError && (
          <span id="title-error" className="text-xs font-medium text-red-500" role="alert">
            {titleError}
          </span>
        )}
      </div>
      <div className="flex flex-col gap-1.5">
        <label htmlFor="todo-description" className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
          Description (optional)
        </label>
        <input
          id="todo-description"
          className="rounded-xl border border-slate-200 bg-slate-50/80 px-3.5 py-2.5 text-sm outline-none transition-all placeholder:text-slate-400 focus:border-primary-400 focus:bg-white focus:ring-4 focus:ring-primary-500/10"
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add more detail..."
          maxLength={1000}
        />
      </div>
      <CategorySelect value={categoryId} onChange={setCategoryId} />
      <button
        className="w-full rounded-xl bg-gradient-to-r from-primary-600 via-primary-500 to-accent-500 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-primary-500/30 transition-all hover:shadow-xl hover:shadow-primary-500/40 hover:brightness-110 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
        type="submit"
        disabled={isLoading}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Adding…
          </span>
        ) : (
          'Add Todo'
        )}
      </button>
    </form>
  )
}
