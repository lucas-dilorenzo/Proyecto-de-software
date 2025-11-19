import { BaseApi } from '../BaseApi'
import { UserResponse } from './types'

export class AuthApi extends BaseApi {
  constructor() {
    super('/auth')
  }

  login(email: string, password: string) {
    return this.request('/login_jwt', { method: 'POST', body: { email, password } })
  }

  logout() {
    return this.request('/logout_jwt')
  }

  getCurrentUser() {
    return this.request<UserResponse>('/user_jwt')
  }
}
