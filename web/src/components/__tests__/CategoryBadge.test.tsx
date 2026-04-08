import { render, screen } from '@testing-library/react'
import { CategoryBadge } from '../CategoryBadge'

describe('CategoryBadge', () => {
  it('renders the category name when provided', () => {
    render(<CategoryBadge categoryName="Work" />)

    expect(screen.getByText('Work')).toBeInTheDocument()
  })

  it('renders nothing when categoryName is null', () => {
    const { container } = render(<CategoryBadge categoryName={null} />)

    expect(container.innerHTML).toBe('')
  })
})
