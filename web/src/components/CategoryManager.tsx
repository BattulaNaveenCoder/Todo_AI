import { useState } from 'react'
import { useCategories, useCreateCategory, useDeleteCategory } from '@/hooks/useCategories'

export const CategoryManager = () => {
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const { data: categories, isLoading, isError } = useCategories()
  const createCategory = useCreateCategory()
  const deleteCategory = useDeleteCategory()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = name.trim()
    if (!trimmed) {
      setError('Name is required.')
      return
    }
    setError('')
    createCategory.mutate(
      { name: trimmed },
      {
        onSuccess: () => setName(''),
        onError: (err) => {
          if (err && typeof err === 'object' && 'response' in err) {
            const axiosErr = err as { response?: { status?: number } }
            if (axiosErr.response?.status === 409) {
              setError('A category with that name already exists.')
              return
            }
          }
          setError('Failed to create category.')
        },
      },
    )
  }

  return (
    <div className="group rounded-2xl border border-white/60 bg-white/70 shadow-lg shadow-slate-200/50 backdrop-blur-xl transition-all animate-slide-up">
      {/* Toggle header */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between px-5 py-4 text-left"
      >
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 shadow-md shadow-primary-500/25">
            <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.568 3H5.25A2.25 2.25 0 0 0 3 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 0 0 5.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 0 0 9.568 3Z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 6h.008v.008H6V6Z" />
            </svg>
          </div>
          <span className="text-sm font-semibold text-slate-800">Categories</span>
          {categories && categories.length > 0 && (
            <span className="rounded-full bg-primary-100 px-2 py-0.5 text-[0.65rem] font-bold text-primary-600">
              {categories.length}
            </span>
          )}
        </div>
        <svg
          className={`h-4 w-4 text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
        </svg>
      </button>

      {/* Expandable content */}
      <div
        className={`grid transition-all duration-300 ease-out ${isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}
      >
        <div className="overflow-hidden">
          <div className="space-y-3 border-t border-slate-100 px-5 pb-5 pt-4">
            <form className="flex gap-2" onSubmit={handleSubmit} noValidate>
              <input
                className="flex-1 rounded-xl border border-slate-200 bg-slate-50/80 px-3.5 py-2.5 text-sm outline-none transition-all placeholder:text-slate-400 focus:border-primary-400 focus:bg-white focus:ring-4 focus:ring-primary-500/10"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="New category name…"
                maxLength={100}
                aria-label="Category name"
              />
              <button
                className="shrink-0 rounded-xl bg-gradient-to-r from-primary-600 to-primary-500 px-5 py-2.5 text-sm font-semibold text-white shadow-md shadow-primary-500/25 transition-all hover:shadow-lg hover:shadow-primary-500/30 hover:brightness-110 active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-50"
                type="submit"
                disabled={createCategory.isPending}
              >
                {createCategory.isPending ? 'Adding…' : 'Add'}
              </button>
            </form>
            {error && (
              <span className="text-xs font-medium text-red-500" role="alert">
                {error}
              </span>
            )}
            {isLoading && <span className="text-xs text-slate-400">Loading…</span>}
            {isError && <span className="text-xs text-slate-400">Failed to load categories.</span>}
            {categories && categories.length > 0 && (
              <ul className="flex flex-wrap gap-2">
                {categories.map((cat) => (
                  <li
                    key={cat.id}
                    className="group/chip inline-flex animate-scale-in items-center gap-1.5 rounded-full border border-primary-200/80 bg-gradient-to-r from-primary-50 to-primary-100/60 px-3 py-1.5 text-xs font-semibold text-primary-700 transition-all hover:shadow-md hover:shadow-primary-200/40"
                  >
                    {cat.name}
                    <button
                      className="flex h-4 w-4 items-center justify-center rounded-full text-primary-400 transition-all hover:bg-primary-200 hover:text-primary-700"
                      onClick={() => deleteCategory.mutate(cat.id)}
                      aria-label={`Delete category "${cat.name}"`}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}
            {categories && categories.length === 0 && (
              <p className="py-2 text-center text-xs text-slate-400">
                No categories yet — add one above!
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
