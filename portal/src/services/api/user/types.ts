import { PaginationQuery } from '../types'

export interface GetTokenData {
  user: string
  password: string
}

export type GetFavoritesQueryParams = PaginationQuery

export interface TokenResponse {
  token: string
  expires_in: number
}
