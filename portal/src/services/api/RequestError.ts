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
