<template>
  <div>
    <header class="topbar">
      <div class="col d-flex justify-content-between align-items-center">
        <div class="col-md-1">
          Portal Público
        </div>
        <div class="col-md-10"></div>
        <div class="col-md-1">
          <router-link to="/login">Login</router-link>
        </div>
      </div>  
    </header>
    <div class="container"><router-view /></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

onMounted(async () => {
  console.log('✅ App mounted');
  // Intentar recuperar la sesión al cargar la aplicación
  try {
    await authStore.fetchCurrentUser();
    console.log('✅ Sesión recuperada');
  } catch {
    console.log('ℹ️ No hay sesión activa');
  }
});
</script>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  background: #fff;
  border-bottom: 1px solid #eee;
  padding: 12px 16px;
  font-weight: 600;
  z-index: 10;
}
</style>
