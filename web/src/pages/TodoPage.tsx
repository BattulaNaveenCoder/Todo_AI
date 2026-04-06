import styles from './TodoPage.module.css'
import { TodoForm } from '@/components/TodoForm'
import { TodoList } from '@/components/TodoList'
import { useCreateTodo } from '@/hooks/useTodos'

const TodoPage = () => {
  const createTodo = useCreateTodo()

  return (
    <div className={styles.page}>
      <h1 className={styles.heading}>My Todos</h1>
      <TodoForm
        onSubmit={(data) => createTodo.mutate(data)}
        isLoading={createTodo.isPending}
      />
      <section aria-label="Todo list" className={styles.listSection}>
        <TodoList />
      </section>
    </div>
  )
}

export default TodoPage
