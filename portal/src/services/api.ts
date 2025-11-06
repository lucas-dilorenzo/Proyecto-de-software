// src/services/api.ts
export const API_BASE: string =
  import.meta.env.VITE_API_BASE || 'https://admin-grupo37.proyecto2025.linti.unlp.edu.ar/api'

type OrderBy = 'rating-5-1' | 'rating-1-5' | 'latest' | 'oldest'

export interface Site {
  id: number
  name: string
  city: string
  province: string
  avg_rating?: number
  cover_image?: string
}

interface ListResponse<T> {
  data: T[]
  page: number
  per_page: number
  total: number
}

interface RequestOptions {
  method?: string
  params?: Record<string, string | number | boolean | undefined>
  auth?: boolean
}

async function request<T>(
  path: string,
  { method = 'GET', params, auth = false }: RequestOptions = {},
): Promise<T> {
  const url = new URL(API_BASE + path)

  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v))
    })
  }

  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth) {
    const token = localStorage.getItem('token')
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(url.toString(), { method, headers, credentials: 'include' })
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`)
  return res.json() as Promise<T>
}

export const SitesAPI = {
  list({
    order_by = 'latest',
    page = 1,
    per_page = 12,
    name,
    city,
    province,
  }: {
    order_by?: OrderBy
    page?: number
    per_page?: number
    name?: string
    city?: string
    province?: string
  }) {
    return request<ListResponse<Site>>('/sites', {
      params: { order_by, page, per_page, name, city, province },
    })
  },

  favorites({ page = 1, per_page = 12 }: { page?: number; per_page?: number }) {
    return request<ListResponse<Site>>('/me/favorites', { params: { page, per_page }, auth: true })
  },
}
