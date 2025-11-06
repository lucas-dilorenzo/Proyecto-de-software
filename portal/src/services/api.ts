// src/services/api.ts

// Base configurable por .env (VITE_API_BASE="/api" con proxy de Vite, o URL absoluta)
export const API_BASE: string = String(import.meta.env.VITE_API_BASE ?? '/api').replace(/\/+$/, '')

export type OrderBy = 'rating-5-1' | 'rating-1-5' | 'latest' | 'oldest'

export interface Site {
  id: number
  name: string
  city: string
  province: string
  // el backend puede enviar cualquiera de estos
  rating?: number
  avg_rating?: number
  cover_url?: string
  cover_image?: string
}

export interface ListResponse<T> {
  data: T[]
  page: number
  per_page: number
  total: number
}

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
type QueryParams = Record<string, string | number | boolean | null | undefined>

interface RequestOptions {
  method?: HttpMethod
  params?: QueryParams
  auth?: boolean
  body?: unknown
}

function buildUrl(path: string, params?: QueryParams): URL {
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  const isAbsolute = /^https?:\/\//i.test(API_BASE)
  const url = isAbsolute
    ? new URL(`${API_BASE}${cleanPath}`)
    : new URL(`${API_BASE}${cleanPath}`, window.location.origin)

  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v))
    })
  }
  return url
}

async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const { method = 'GET', params, auth = false, body } = opts
  const url = buildUrl(path, params)

  // Logs útiles mientras debugueamos
  console.log('🌐 API_BASE:', API_BASE)
  console.log('📡 Fetching:', url.toString())

  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth) {
    const token = localStorage.getItem('token')
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(url.toString(), {
    method,
    headers,
    credentials: 'include',
    body: body ? JSON.stringify(body) : undefined,
  })

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
