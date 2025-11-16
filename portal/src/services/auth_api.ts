import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/auth'; // Reemplaza con la URL real de tu API

const apiAxios = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true // Habilita el envío de cookies en las solicitudes
});

export const authApi = {
  async login(email: string, password: string) {
    const response = await apiAxios.post(`${API_BASE_URL}/login_jwt`, {
      email,
      password
    });
    return response.data;
  },

  async logout() {
    const response = await apiAxios.get(`${API_BASE_URL}/logout_jwt`);
    return response.data;
  },
  async getCurrentUser() {
    const response = await apiAxios.get(`${API_BASE_URL}/user_jwt`);
    return response.data;
  }
};