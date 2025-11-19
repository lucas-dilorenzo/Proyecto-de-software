import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: {
      usuario: '',
      email: '',
      id: '',
      token: '',
    },
    isLoggedIn: false,
  }),
  actions: {
    async loginUser(payload: { email: string; password: string }) {
      await api
        .getAuthApi()
        .login(payload.email, payload.password)
        .then(() => {
          // Guardar el token JWT
          // this.user.token = response.access_token;
        })
      // Después del login, obtener los datos del usuario desde el backend
      await this.fetchCurrentUser()
    },
    async logoutUser() {
      await api.getAuthApi().logout()
      this.user = {
        usuario: '',
        email: '',
        id: '',
        token: '',
      }
      this.isLoggedIn = false
    },
    async fetchCurrentUser() {
      try {
        const userData = await api.getAuthApi().getCurrentUser()
        this.user = {
          usuario: userData.nombre || userData.usuario,
          email: userData.email,
          id: userData.id,
          token: userData.token || '',
        }
        this.isLoggedIn = true
      } catch (error) {
        // Si falla la autenticación, limpiar el estado
        this.user = {
          usuario: '',
          email: '',
          id: '',
          token: '',
        }
        this.isLoggedIn = false
        throw error
      }
    },
  },
})
