import { BaseApi } from '../../BaseApi'
import type { CreateReviewData, ListReviewsQueryParams } from './types'

export class ReviewsApi extends BaseApi {
  constructor(siteId: number) {
    super(`/sites/${siteId}/reviews`)
  }

  list(query?: ListReviewsQueryParams) {
    return this.request(`/`, { query })
  }

  create(data: CreateReviewData, token: string) {
    return this.request(`/`, { method: 'POST', body: data, token })
  }

  get(id: number, token: string) {
    return this.request(`/${id}`, { token })
  }

  delete(id: number, token: string) {
    return this.request(`/${id}`, { method: 'DELETE', token })
  }
}
