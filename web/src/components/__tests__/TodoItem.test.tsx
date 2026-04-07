import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TodoItem } from '../TodoItem'
import type { Todo } from '@/types'

const makeTodo = (overrides: Partial<Todo> = {}): Todo => ({
  id: 1,
  title: 'Test todo',
  description: null,
  isCompleted: false,
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T00:00:00Z',
  ...overrides,
})

describe('TodoItem', () => {
  it('renders the todo title', () => {
    const todo = makeTodo({ title: 'Buy milk' })

    render(<TodoItem todo={todo} onToggle={vi.fn()} onDelete={vi.fn()} />)

    expect(screen.getByText('Buy milk')).toBeInTheDocument()
  })

  it('renders the description when present', () => {
    const todo = makeTodo({ description: 'From the local shop' })

    render(<TodoItem todo={todo} onToggle={vi.fn()} onDelete={vi.fn()} />)

    expect(screen.getByText('From the local shop')).toBeInTheDocument()
  })

  it('does not render description element when description is null', () => {
    const todo = makeTodo({ description: null })

    render(<TodoItem todo={todo} onToggle={vi.fn()} onDelete={vi.fn()} />)

    expect(screen.queryByRole('presentation')).not.toBeInTheDocument()
  })

  it('calls onDelete with the correct id when delete button is clicked', async () => {
    const user = userEvent.setup()
    const onDelete = vi.fn()
    const todo = makeTodo({ id: 42 })

    render(<TodoItem todo={todo} onToggle={vi.fn()} onDelete={onDelete} />)
    await user.click(screen.getByRole('button', { name: /delete/i }))

    expect(onDelete).toHaveBeenCalledTimes(1)
    expect(onDelete).toHaveBeenCalledWith(42)
  })

  it('calls onToggle with the correct id when checkbox is clicked', async () => {
    const user = userEvent.setup()
    const onToggle = vi.fn()
    const todo = makeTodo({ id: 7, isCompleted: false })

    render(<TodoItem todo={todo} onToggle={onToggle} onDelete={vi.fn()} />)
    await user.click(screen.getByRole('checkbox'))

    expect(onToggle).toHaveBeenCalledTimes(1)
    expect(onToggle).toHaveBeenCalledWith(7)
  })

  it('renders the checkbox as checked when todo is completed', () => {
    const todo = makeTodo({ isCompleted: true })

    render(<TodoItem todo={todo} onToggle={vi.fn()} onDelete={vi.fn()} />)

    expect(screen.getByRole('checkbox')).toBeChecked()
  })

  it('renders the checkbox as unchecked when todo is not completed', () => {
    const todo = makeTodo({ isCompleted: false })

    render(<TodoItem todo={todo} onToggle={vi.fn()} onDelete={vi.fn()} />)

    expect(screen.getByRole('checkbox')).not.toBeChecked()
  })
})
