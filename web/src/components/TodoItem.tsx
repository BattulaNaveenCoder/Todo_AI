import styles from './TodoItem.module.css'
import type { Todo } from '@/types'

interface TodoItemProps {
  todo: Todo
  onToggle: (id: number) => void
  onDelete: (id: number) => void
}

export const TodoItem = ({ todo, onToggle, onDelete }: TodoItemProps) => {
  return (
    <li className={`${styles.item} ${todo.isCompleted ? styles.completed : ''}`}>
      <input
        type="checkbox"
        checked={todo.isCompleted}
        onChange={() => onToggle(todo.id)}
        aria-label={`Mark "${todo.title}" as ${todo.isCompleted ? 'incomplete' : 'complete'}`}
      />
      <div className={styles.content}>
        <span className={styles.title}>{todo.title}</span>
        {todo.description && (
          <span className={styles.description}>{todo.description}</span>
        )}
      </div>
      <button
        className={styles.deleteButton}
        onClick={() => onDelete(todo.id)}
        aria-label={`Delete "${todo.title}"`}
      >
        Delete
      </button>
    </li>
  )
}
