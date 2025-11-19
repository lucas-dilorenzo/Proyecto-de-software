import { OrderBy, PaginationQuery } from '../types'

export interface Site {
  id: number
  name: string
  description_short: string
  description: string
  city: string
  province: string
  latitude: number
  longitude: number
  tags: string[]
  conservation_status: string
  inserted_at: Date
  updated_at: Date
  avg_rating?: number
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
  tags?: string // Comma-separated string, e.g. "histórico,religioso"
  order_by?: OrderBy
  lat?: number
  long?: number
  radius?: number
}

export type CreateSiteData = Omit<Site, 'id' | 'inserted_at' | 'updated_at'>
