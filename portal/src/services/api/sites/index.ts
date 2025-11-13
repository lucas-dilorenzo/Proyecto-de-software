import { BaseApi } from '../BaseApi'
import type { ListSitesQueryParams } from './types'

export class SitesApi extends BaseApi {
  constructor() {
    super('/sites')
  }

  list(query?: ListSitesQueryParams) {
    return this.request('/', { query })
  }

  get(id: number) {
    return this.request(`/${id}`)
  }

  create(data: object, token: string) {
    return this.request('/', { method: 'POST', body: data, token })
  }

  // FAVORITES

  star(id: number, token: string) {
    return this.request(`/${id}/favorite`, { method: 'PUT', token })
  }

  unstar(id: number, token: string) {
    return this.request(`/${id}/favorite`, { method: 'DELETE', token })
  }
}
