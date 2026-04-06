export interface Todo {
  id: number
  title: string
  description: string | null
  isCompleted: boolean
  createdAt: string
  updatedAt: string
}

export interface TodoCreate {
  title: string
  description?: string
}

export interface TodoUpdate {
  title?: string
  description?: string
  isCompleted?: boolean
}
