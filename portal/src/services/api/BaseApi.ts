import { RequestError } from './RequestError'
import type { PaginatedResponse, RequestOptions } from './types'

// Base configurable por .env (VITE_API_BASE="/api" con proxy de Vite, o URL absoluta)
export const API_BASE: string = String(import.meta.env?.VITE_API_BASE ?? '/api').replace(/\/+$/, '')

export class BaseApi {
  baseUrl: string

  constructor(basePath: string) {
    this.baseUrl = API_BASE + basePath.replace(/\/+$/, '')
  }

  protected async request<T, Paginated extends boolean = false>(
    path: string,
    options?: RequestOptions,
  ): Promise<Paginated extends true ? PaginatedResponse<T> : T> {
    const { method = 'GET', body, query, token } = options ?? {}
    const queryParams = new URLSearchParams()
    if (query) {
      Object.entries(query).forEach(
        ([key, value]) => value !== undefined && queryParams.set(key, String(value)),
      )
    }
    const headers: HeadersInit = {}
    if (token) headers['Authorization'] = `Bearer ${token}`
    if (body) headers['Content-Type'] = "application/json"
    const url = `${this.baseUrl}${path}` + (queryParams.size ? `?${queryParams.toString()}` : '')
    const response = await fetch(url, {
      method,
      body: body && JSON.stringify(body),
      headers,
      credentials: 'include',
    })
    if (response.ok) {
      if (response.status != 204) return await response.json()
      else return undefined as Paginated extends true ? PaginatedResponse<T> : T
    } else throw new RequestError({ status: response.status, ...(await response.json()) })
  }
  }
