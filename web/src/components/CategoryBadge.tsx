interface CategoryBadgeProps {
  categoryName: string | null
}

export const CategoryBadge = ({ categoryName }: CategoryBadgeProps) => {
  if (!categoryName) {
    return null
  }

  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-gradient-to-r from-primary-50 to-primary-100/70 px-2.5 py-0.5 text-[0.65rem] font-semibold text-primary-600 ring-1 ring-inset ring-primary-200/60">
      <span className="h-1.5 w-1.5 rounded-full bg-primary-400" />
      {categoryName}
    </span>
  )
}
