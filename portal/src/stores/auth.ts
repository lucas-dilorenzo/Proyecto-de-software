import { defineStore } from 'pinia';
import { authApi } from '@/services/auth_api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: {
      usuario: '',
      email: '',
      id: '',
      token: ''
    },
    isLoggedIn: false
  }),
  actions: {
  async loginUser(payload: { email: string; password: string }) {
    await authApi.login(payload.email, payload.password).then((response) => {
      // Guardar el token JWT
      this.user.token = response.access_token;
    });
    // Después del login, obtener los datos del usuario desde el backend
    await this.fetchCurrentUser();
  },
    async logoutUser() {
        await authApi.logout();
        this.user = {
            usuario: '',
            email: '',
            id: '',
            token: ''
        };
        this.isLoggedIn = false;
    },
    async fetchCurrentUser() {
        try {
            const userData = await authApi.getCurrentUser();
            this.user = {
                usuario: userData.nombre || userData.usuario,
                email: userData.email,
                id: userData.id,
                token: userData.token || ''
            };
            this.isLoggedIn = true;
        } catch (error) {
            // Si falla la autenticación, limpiar el estado
            this.user = {
                usuario: '',
                email: '',
                id: '',
                token: ''
            };
            this.isLoggedIn = false;
            throw error;
        }
    }
  }
});
