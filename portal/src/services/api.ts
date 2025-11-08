// src/services/api.ts

// Base configurable por .env (VITE_API_BASE="/api" con proxy de Vite, o URL absoluta)
export const API_BASE: string = String(import.meta.env.VITE_API_BASE ?? '/api').replace(/\/+$/, '')

export type OrderBy = 'rating-5-1' | 'rating-1-5' | 'latest' | 'oldest'

export interface Site {
  id: number
  name: string
  city: string
  province: string
  latitude: number  // 🔹 Agregado
  longitude: number  // 🔹 Agregado
  description?: string  // 🔹 Agregado
  conservation_status?: string  // 🔹 Agregado
  rating?: number
  avg_rating?: number
  cover_url?: string
  cover_image?: string
  tags?: string[]  // 🔹 Agregado
  images?: SiteImage[]  // 🔹 Agregado
}

// 🔹 Nueva interfaz para imágenes
export interface SiteImage {
  id: number
  url: string
  titulo?: string
  descripcion?: string
  order?: number
}

export interface PaginatedResponse<T> {
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
  async list(params: {
    name?: string
    description?: string
    city?: string
    province?: string
    tags?: string
    lat?: number
    long?: number
    radius?: number
    order_by?: OrderBy
    page?: number
    per_page?: number
  }): Promise<PaginatedResponse<Site>> {
    const query = new URLSearchParams()
    if (params.name) query.set('name', params.name)
    if (params.description) query.set('description', params.description)
    if (params.city) query.set('city', params.city)
    if (params.province) query.set('province', params.province)
    if (params.tags) query.set('tags', params.tags)
    if (params.lat !== undefined) query.set('lat', String(params.lat))
    if (params.long !== undefined) query.set('long', String(params.long))
    if (params.radius !== undefined) query.set('radius', String(params.radius))
    if (params.order_by) query.set('order_by', params.order_by)
    if (params.page) query.set('page', String(params.page))
    if (params.per_page) query.set('per_page', String(params.per_page))

    const url = `${API_BASE}/sites?${query}`
    const res = await fetch(url)
    if (!res.ok) throw new Error('Error al obtener sitios')
    return res.json()
  },

  // 🔹 Nuevo método para obtener un sitio por ID
  async getById(id: number): Promise<Site> {
    const url = `${API_BASE}/sites/${id}`
    const res = await fetch(url)
    if (!res.ok) {
      if (res.status === 404) throw new Error('Sitio no encontrado')
      throw new Error('Error al obtener el sitio')
    }
    return res.json()
  },

  async favorites(params: {
    page?: number
    per_page?: number
  }): Promise<PaginatedResponse<Site>> {
    const query = new URLSearchParams()
    if (params.page) query.set('page', String(params.page))
    if (params.per_page) query.set('per_page', String(params.per_page))

    const url = `${API_BASE}/me/favorites?${query}`
    const res = await fetch(url, { credentials: 'include' })
    if (!res.ok) throw new Error('Error al obtener favoritos')
    return res.json()
  },
}
