import { BaseApi } from '../BaseApi'
import type { CreateSiteData, ListSitesQueryParams, Site } from './types'

export class SitesApi extends BaseApi {
  constructor() {
    super('/sites')
  }

  list(query?: ListSitesQueryParams) {
    return this.request<Site, true>('/', { query })
  }

  get(id: number) {
    return this.request<Site>(`/${id}`)
  }

  create(data: CreateSiteData, token: string) {
    return this.request<Site & { user_id: number }>('/', { method: 'POST', body: data, token })
  }

  // FAVORITES

  star(id: number, token: string) {
    return this.request<void>(`/${id}/favorite`, { method: 'PUT', token })
  }

  unstar(id: number, token: string) {
    return this.request<void>(`/${id}/favorite`, { method: 'DELETE', token })
  }
}
