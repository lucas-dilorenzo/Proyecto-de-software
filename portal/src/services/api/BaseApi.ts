import type { RequestOptions } from './types'

// Base configurable por .env (VITE_API_BASE="/api" con proxy de Vite, o URL absoluta)
export const API_BASE: string = String(import.meta.env?.VITE_API_BASE ?? '/api').replace(/\/+$/, '')

export class RequestError extends Error {
  status: number
  code: string
  message: string
  details?: Record<string, string[]>

  constructor(error: {
    status: number
    code: string
    message: string
    details?: Record<string, string[]>
  }) {
    super()
    this.status = error.status
    this.code = error.code
    this.message = error.message
    this.details = error.details
  }
}

export class BaseApi {
  baseUrl: string

  constructor(basePath: string) {
    this.baseUrl = API_BASE + basePath.replace(/\/+$/, '')
  }

  async request(path: string, options?: RequestOptions) {
    const { method = 'GET', body, query, token } = options ?? {}
    const queryParams = new URLSearchParams()
    if (query) {
      Object.entries(query).forEach(
        ([key, value]) => value !== undefined && queryParams.set(key, String(value)),
      )
    }
    // console.dir(
    //   {
    //     method,
    //     url: `${this.baseUrl}${path}?${queryParams.toString()}`,
    //     token,
    //     body,
    //   },
    //   { depth: Infinity },
    // )
    const response = await fetch(`${this.baseUrl}${path}?${queryParams.toString()}`, {
      method,
      body: String(body),
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    })
    if (response.ok) return response.json()
    else throw new RequestError(await response.json())
  }
}
