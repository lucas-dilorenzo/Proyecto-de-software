import { BaseApi } from '../BaseApi'
import type { GetFavoritesQueryParams, GetTokenData } from './types'

export class UserApi extends BaseApi {
  constructor() {
    super('/')
  }

  getToken(data: GetTokenData) {
    return this.request('/api/auth', { method: 'POST', body: data })
  }

  getFavorites(query: GetFavoritesQueryParams, token: string) {
    return this.request('/me/favorites', { query, token })
  }
}
