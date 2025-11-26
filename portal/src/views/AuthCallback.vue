<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  const params = new URLSearchParams(window.location.search);
  const accessToken = params.get('access_token');
  const userId = params.get('user_id');

  if (accessToken && userId) {
    // Guardar el token en la store de Pinia
    authStore.user.token = accessToken;
    authStore.user.id = userId;
    
    // También guardarlo en localStorage como backup
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('user_id', userId);
    
    // Obtener datos completos del usuario desde el backend
    try {
      await authStore.fetchCurrentUser();
      // Redirigir al home o dashboard
      router.replace({ name: 'home' });
    } catch (error) {
      console.error('Error al obtener datos del usuario:', error);
      router.replace({ name: 'login' });
    }
  } else {
    router.replace({ name: 'login' });
  }
});
</script>

<template>
  <div>
    <p>Procesando autenticación...</p>
  </div>
</template>
