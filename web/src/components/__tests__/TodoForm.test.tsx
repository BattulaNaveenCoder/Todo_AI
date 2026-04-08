import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { TodoForm } from '../TodoForm'
import type { TodoCreate } from '@/types'

vi.mock('@/hooks/useCategories', () => ({
  useCategories: vi.fn(() => ({
    data: [],
    isLoading: false,
    isError: false,
  })),
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('TodoForm', () => {
  it('renders the title input and submit button', () => {
    render(<TodoForm onSubmit={vi.fn()} isLoading={false} />, { wrapper: createWrapper() })

    expect(screen.getByLabelText(/title/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /add todo/i })).toBeInTheDocument()
  })

  it('shows an error message when submitted with an empty title', async () => {
    const user = userEvent.setup()
    render(<TodoForm onSubmit={vi.fn()} isLoading={false} />, { wrapper: createWrapper() })

    await user.click(screen.getByRole('button', { name: /add todo/i }))

    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveTextContent(/title is required/i)
  })

  it('does not call onSubmit when title is empty', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<TodoForm onSubmit={onSubmit} isLoading={false} />, { wrapper: createWrapper() })

    await user.click(screen.getByRole('button', { name: /add todo/i }))

    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('does not call onSubmit when title is only whitespace', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<TodoForm onSubmit={onSubmit} isLoading={false} />, { wrapper: createWrapper() })

    await user.type(screen.getByLabelText(/title/i), '   ')
    await user.click(screen.getByRole('button', { name: /add todo/i }))

    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('calls onSubmit with trimmed title when form is valid', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<TodoForm onSubmit={onSubmit} isLoading={false} />, { wrapper: createWrapper() })

    await user.type(screen.getByLabelText(/title/i), '  Buy groceries  ')
    await user.click(screen.getByRole('button', { name: /add todo/i }))

    expect(onSubmit).toHaveBeenCalledTimes(1)
    const payload: TodoCreate = onSubmit.mock.calls[0][0]
    expect(payload.title).toBe('Buy groceries')
  })

  it('includes description in the payload when filled in', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<TodoForm onSubmit={onSubmit} isLoading={false} />, { wrapper: createWrapper() })

    await user.type(screen.getByLabelText(/title/i), 'Task')
    await user.type(screen.getByLabelText(/description/i), 'Some detail')
    await user.click(screen.getByRole('button', { name: /add todo/i }))

    const payload: TodoCreate = onSubmit.mock.calls[0][0]
    expect(payload.description).toBe('Some detail')
  })

  it('clears the form inputs after a successful submission', async () => {
    const user = userEvent.setup()
    render(<TodoForm onSubmit={vi.fn()} isLoading={false} />, { wrapper: createWrapper() })
    const titleInput = screen.getByLabelText(/title/i)

    await user.type(titleInput, 'Some task')
    await user.click(screen.getByRole('button', { name: /add todo/i }))

    expect(titleInput).toHaveValue('')
  })

  it('disables the submit button when isLoading is true', () => {
    render(<TodoForm onSubmit={vi.fn()} isLoading={true} />, { wrapper: createWrapper() })

    expect(screen.getByRole('button', { name: /adding/i })).toBeDisabled()
  })
})
