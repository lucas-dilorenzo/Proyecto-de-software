import { OrderBy, PaginationQuery } from '../types'

export interface Site {
  id: number
  name: string
  short_description: string
  description: string
  city: string
  province: string
  lat: number
  long: number
  tags: string[]
  state_of_conservation: string
  inserted_at: Date
  updated_at: Date
  cover_url?: string
  cover_image?: string
  images?: SiteImage[]
}

export interface SiteImage {
  id: number
  url: string
  titulo?: string
  descripcion?: string
  order?: number
}

export type ListSitesQueryParams = PaginationQuery & {
  name?: string
  description?: string
  city?: string
  province?: string
  tags?: string[]
  order_by?: OrderBy
  lat?: number
  long?: number
  radius?: number
}

export type CreateSiteData = Omit<Site, 'id' | 'inserted_at' | 'updated_at'>
