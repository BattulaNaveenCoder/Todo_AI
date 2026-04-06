import { useState } from 'react'
import styles from './TodoForm.module.css'
import type { TodoCreate } from '@/types'

interface TodoFormProps {
  onSubmit: (data: TodoCreate) => void
  isLoading: boolean
}

export const TodoForm = ({ onSubmit, isLoading }: TodoFormProps) => {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [titleError, setTitleError] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) {
      setTitleError('Title is required.')
      return
    }
    setTitleError('')
    onSubmit({ title: title.trim(), description: description.trim() || undefined })
    setTitle('')
    setDescription('')
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      <div className={styles.field}>
        <label htmlFor="todo-title" className={styles.label}>
          Title
        </label>
        <input
          id="todo-title"
          className={styles.input}
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs to be done?"
          maxLength={255}
          aria-describedby={titleError ? 'title-error' : undefined}
        />
        {titleError && (
          <span id="title-error" className={styles.error} role="alert">
            {titleError}
          </span>
        )}
      </div>
      <div className={styles.field}>
        <label htmlFor="todo-description" className={styles.label}>
          Description (optional)
        </label>
        <input
          id="todo-description"
          className={styles.input}
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add more detail..."
          maxLength={1000}
        />
      </div>
      <button
        className={styles.submitButton}
        type="submit"
        disabled={isLoading}
      >
        {isLoading ? 'Adding…' : 'Add Todo'}
      </button>
    </form>
  )
}
