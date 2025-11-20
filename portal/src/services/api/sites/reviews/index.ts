import { BaseApi } from '../../BaseApi'
import type { Review, CreateReviewData, ListReviewsQueryParams } from './types'

export class ReviewsApi extends BaseApi {
  constructor(siteId: number) {
    super(`/sites/${siteId}/reviews`)
  }

  list(query?: ListReviewsQueryParams) {
    return this.request<Review, true>(``, { query })
  }

  create(data: CreateReviewData, token: string) {
    return this.request<Review>(``, { method: 'POST', body: data, token })
  }

  get(id: number, token: string) {
    return this.request<Review>(`/${id}`, { token })
  }

  delete(id: number, token: string) {
    return this.request<void>(`/${id}`, { method: 'DELETE', token })
  }
}
