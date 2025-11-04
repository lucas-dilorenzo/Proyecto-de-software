// src/services/api.ts
export const API_BASE: string = import.meta.env.VITE_API_BASE || '/api'

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
type QueryParams = Record<string, string | number | boolean | null | undefined>

interface RequestOptions {
  method?: HttpMethod
  params?: QueryParams
  body?: unknown
  auth?: boolean
}

async function request<T>(
  path: string,
  { method = 'GET', params, body, auth = false }: RequestOptions = {},
): Promise<T> {
  const url = new URL(API_BASE + path, window.location.origin)

  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v))
    })
  }

  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth) {
    // headers['Authorization'] = `Bearer ${token}`;
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

// ---- Tipos de dominio (ajustá a tu API real)
export interface Site {
  id: number
  name: string
  city: string
  province: string
  rating?: number
  cover_url?: string
}

interface ListResponse<T> {
  items: T[]
}

// ---- Endpoints
export const SitesAPI = {
  list({ sort, limit = 10 }: { sort?: 'visited' | 'rating' | 'recent'; limit?: number }) {
    return request<ListResponse<Site>>('/sites', { params: { sort, limit } })
  },
  favorites({ limit = 10 }: { limit?: number }) {
    return request<ListResponse<Site>>('/sites/favorites', { params: { limit }, auth: true })
  },
}
