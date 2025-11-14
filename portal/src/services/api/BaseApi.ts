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
    const url = `${this.baseUrl}${path}` + (queryParams.size ? `?${queryParams.toString()}` : '')
    // console.dir(
    //   {
    //     method,
    //     url,
    //     token,
    //     body,
    //   },
    //   { depth: Infinity },
    // )
    const response = await fetch(url, {
      method,
      body: String(body),
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    })
    const responseBody = await response.json()
    if (response.ok) return responseBody
    else throw new RequestError({ status: response.status, ...responseBody })
  }
}
