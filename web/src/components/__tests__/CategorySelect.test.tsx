import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { CategorySelect } from '../CategorySelect'
import type { Category } from '@/types'

const mockCategories: Category[] = [
  { id: 1, name: 'Work', createdAt: '2024-01-01T00:00:00Z', updatedAt: '2024-01-01T00:00:00Z' },
  { id: 2, name: 'Personal', createdAt: '2024-01-01T00:00:00Z', updatedAt: '2024-01-01T00:00:00Z' },
]

vi.mock('@/hooks/useCategories', () => ({
  useCategories: vi.fn(() => ({
    data: mockCategories,
    isLoading: false,
    isError: false,
  })),
}))

import { useCategories } from '@/hooks/useCategories'

const mockUseCategories = vi.mocked(useCategories)

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('CategorySelect', () => {
  beforeEach(() => {
    mockUseCategories.mockReturnValue({
      data: mockCategories,
      isLoading: false,
      isError: false,
    } as unknown as ReturnType<typeof useCategories>)
  })

  it('renders the loading state when categories are loading', () => {
    mockUseCategories.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    } as unknown as ReturnType<typeof useCategories>)

    render(<CategorySelect value={undefined} onChange={vi.fn()} />, {
      wrapper: createWrapper(),
    })

    expect(screen.getByText('Loading…')).toBeInTheDocument()
  })

  it('renders "No category" placeholder when no value is selected', () => {
    render(<CategorySelect value={undefined} onChange={vi.fn()} />, {
      wrapper: createWrapper(),
    })

    expect(screen.getByText('No category')).toBeInTheDocument()
  })

  it('renders category options when dropdown is opened', async () => {
    const user = userEvent.setup()

    render(<CategorySelect value={undefined} onChange={vi.fn()} />, {
      wrapper: createWrapper(),
    })

    await user.click(screen.getByRole('button', { expanded: false }))

    expect(screen.getByRole('listbox')).toBeInTheDocument()
    expect(screen.getByText('Work')).toBeInTheDocument()
    expect(screen.getByText('Personal')).toBeInTheDocument()
  })

  it('calls onChange with the correct category id when an option is selected', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(<CategorySelect value={undefined} onChange={onChange} />, {
      wrapper: createWrapper(),
    })

    await user.click(screen.getByRole('button', { expanded: false }))
    await user.click(screen.getByText('Work'))

    expect(onChange).toHaveBeenCalledTimes(1)
    expect(onChange).toHaveBeenCalledWith(1)
  })

  it('calls onChange with undefined when "No category" is selected', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(<CategorySelect value={1} onChange={onChange} />, {
      wrapper: createWrapper(),
    })

    await user.click(screen.getByRole('button', { expanded: false }))

    const noCategories = screen.getAllByText('No category')
    const listboxOption = noCategories.find((el) => el.closest('[role="option"]'))
    await user.click(listboxOption!)

    expect(onChange).toHaveBeenCalledWith(undefined)
  })

  it('shows the selected category name when a value is set', () => {
    render(<CategorySelect value={2} onChange={vi.fn()} />, {
      wrapper: createWrapper(),
    })

    expect(screen.getByText('Personal')).toBeInTheDocument()
  })
})
