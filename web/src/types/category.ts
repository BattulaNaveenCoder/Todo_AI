export interface Category {
  id: number
  name: string
  createdAt: string
  updatedAt: string
}

export interface CategoryCreate {
  name: string
}

export interface CategoryUpdate {
  name?: string
}
