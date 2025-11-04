export const API_BASE: string = import.meta.env.VITE_API_BASE || '/api'

interface RequestOptions {
  method?: string
  params?: Record<string, any>
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
    // Ejemplo: si usan token JWT
    // headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(url.toString(), {
    method,
    headers,
    credentials: 'include',
    body: body ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    throw new Error(`API ${res.status}: ${await res.text()}`)
  }

  return (await res.json()) as T
}

// Interfaces de ejemplo para tus datos
export interface Site {
  id: number
  name: string
  city: string
  province: string
  rating?: number
  cover_url?: string
}

// Endpoints
export const SitesAPI = {
  list({ sort, limit = 10 }: { sort: string; limit?: number }) {
    return request<{ items: Site[] }>('/sites', { params: { sort, limit } })
  },
  favorites({ limit = 10 }: { limit?: number }) {
    return request<{ items: Site[] }>('/sites/favorites', { params: { limit }, auth: true })
  },
}
