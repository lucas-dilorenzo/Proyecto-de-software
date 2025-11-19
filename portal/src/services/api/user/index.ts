import { BaseApi } from '../BaseApi'
import type { Site } from '../sites/types'
import type { GetFavoritesQueryParams, GetTokenData, TokenResponse } from './types'

export class UserApi extends BaseApi {
  constructor() {
    super('/')
  }

  getToken(data: GetTokenData) {
    return this.request<TokenResponse>('/api/auth', { method: 'POST', body: data })
  }

  getFavorites(query: GetFavoritesQueryParams, token: string) {
    return this.request<Site, true>('/me/favorites', { query, token })
  }
  

}
