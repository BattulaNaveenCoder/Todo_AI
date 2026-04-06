import styles from './TodoList.module.css'
import { TodoItem } from './TodoItem'
import { useTodos, useUpdateTodo, useDeleteTodo } from '@/hooks/useTodos'

export const TodoList = () => {
  const { data: todos, isLoading, isError, error } = useTodos()
  const updateTodo = useUpdateTodo()
  const deleteTodo = useDeleteTodo()

  if (isLoading) {
    return <div role="status" className={styles.message}>Loading todos…</div>
  }

  if (isError) {
    return (
      <div role="alert" className={styles.error}>
        Error: {(error as Error).message}
      </div>
    )
  }

  if (!todos?.length) {
    return <div className={styles.message}>No todos yet. Create one!</div>
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
    <ul className={styles.list}>
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
