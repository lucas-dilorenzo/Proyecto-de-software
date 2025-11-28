export interface PaginationQuery {
  page?: number
  per_page?: number
}

export interface PaginatedResponse<T> {
  data: T[]
  page: number
  per_page: number
  total: number
}

export type OrderBy = 'rating-5-1' | 'rating-1-5' | 'latest' | 'oldest' | 'name-a-z' | 'name-z-a'

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE'
export type QueryParams = object

export interface RequestOptions {
  method?: HttpMethod
  query?: QueryParams
  token?: string
  body?: object
}

export type * from './sites/types'
export type * from './sites/reviews/types'
export type * from './user/types'
export type * from './flags/types'
