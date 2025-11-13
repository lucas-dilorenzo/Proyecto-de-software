import { PaginationQuery } from '../types'

export interface GetTokenData {
  user: string
  password: string
}

export type GetFavoritesQueryParams = PaginationQuery
