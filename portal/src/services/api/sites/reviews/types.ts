import { PaginationQuery } from '../../types'

export interface Review {
  id: number
  site_id: number
  rating: number
  comment: string
  state: string
  inserted_at: Date
  updated_at: Date
}

export type ListReviewsQueryParams = PaginationQuery

export type CreateReviewData = Omit<Review, 'id' | 'inserted_at' | 'updated_at'>
