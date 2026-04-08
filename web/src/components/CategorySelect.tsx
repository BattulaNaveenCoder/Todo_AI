import { useState, useRef, useEffect } from 'react'
import { useCategories } from '@/hooks/useCategories'

interface CategorySelectProps {
  value: number | undefined
  onChange: (categoryId: number | undefined) => void
}

export const CategorySelect = ({ value, onChange }: CategorySelectProps) => {
  const { data: categories, isLoading, isError } = useCategories()
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const selected = categories?.find((c) => c.id === value)
  const label = selected ? selected.name : 'No category'

  useEffect(() => {
    const handleOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleOutside)
    return () => document.removeEventListener('mousedown', handleOutside)
  }, [])

  const handleSelect = (id: number | undefined) => {
    onChange(id)
    setIsOpen(false)
  }

  return (
    <div className="flex flex-col gap-1.5" ref={containerRef}>
      <label className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
        Category (optional)
      </label>
      <button
        type="button"
        onClick={() => !isLoading && setIsOpen(!isOpen)}
        disabled={isLoading}
        className={`flex items-center justify-between rounded-xl border px-3.5 py-2.5 text-sm outline-none transition-all ${
          isOpen
            ? 'border-primary-400 bg-white ring-4 ring-primary-500/10'
            : 'border-slate-200 bg-slate-50/80 hover:border-slate-300'
        } disabled:cursor-not-allowed disabled:opacity-50`}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span className={value ? 'text-slate-800' : 'text-slate-400'}>
          {isLoading ? 'Loading…' : label}
        </span>
        <svg
          className={`h-4 w-4 text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
        </svg>
      </button>

      {isOpen && (
        <ul
          role="listbox"
          className="z-20 -mt-1 max-h-48 overflow-auto rounded-xl border border-slate-200 bg-white/90 py-1 shadow-xl shadow-slate-200/50 backdrop-blur-xl animate-scale-in"
        >
          <li
            role="option"
            aria-selected={!value}
            onClick={() => handleSelect(undefined)}
            className={`flex cursor-pointer items-center gap-2 px-3.5 py-2 text-sm transition-colors ${
              !value
                ? 'bg-primary-50 font-medium text-primary-700'
                : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-slate-300" />
            No category
          </li>
          {isError && (
            <li className="px-3.5 py-2 text-xs text-red-400">Failed to load categories</li>
          )}
          {categories?.map((cat) => (
            <li
              key={cat.id}
              role="option"
              aria-selected={value === cat.id}
              onClick={() => handleSelect(cat.id)}
              className={`flex cursor-pointer items-center gap-2 px-3.5 py-2 text-sm transition-colors ${
                value === cat.id
                  ? 'bg-primary-50 font-medium text-primary-700'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <span className="h-1.5 w-1.5 rounded-full bg-primary-400" />
              {cat.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
