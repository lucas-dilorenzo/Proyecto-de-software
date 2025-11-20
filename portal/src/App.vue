<template>
  <AuthProvider>
    <div>
      <header class="topbar">
        <div class="col d-flex justify-content-between align-items-center">
          <div class="col-md-3">
            <router-link
              to="/"
              class="navbar-brand d-flex align-items-center"
              aria-label="Inicio - Patrimonio Histórico"
            >
              <img :src="logo" class="logo-navbar me-2" alt="Patrimonio Histórico logo" />
              <div>
                <span class="fw-bold">Patrimonio Histórico</span>
                <small class="d-block text-muted d-none d-md-block">Explora sitios históricos</small>
              </div>
            </router-link>
          </div>
          <div class="col-md-7"></div>
          <div class="col-md-2 d-flex justify-content-end align-items-center">
            <div v-if="isLoggedIn">
              <UserDropdown :loggedIn="isLoggedIn" />
            </div>
            <router-link v-else to="/login" class="btn btn-outline-primary">
              <i class="bi bi-box-arrow-in-right me-1"></i>
              Iniciar Sesión
            </router-link>
          </div>
        </div>
      </header>
      <div class="container"><router-view /></div>
    </div>
  </AuthProvider>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import UserDropdown from '@/components/UserDropdown.vue'
import AuthProvider from './components/auth/AuthProvider.vue'
import logo from '@/assets/logo.svg'

const authStore = useAuthStore()
const isLoggedIn = computed(() => authStore.isLoggedIn)

onMounted(async () => {
  console.log('✅ App mounted')
  // Intentar recuperar la sesión al cargar la aplicación
  try {
    await authStore.fetchCurrentUser()
    console.log('✅ Sesión recuperada')
  } catch {
    console.log('ℹ️ No hay sesión activa')
  }
})
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

.logo-navbar {
  width: 42px;
  height: 42px;
  display: inline-block;
}

.navbar-brand .fw-bold {
  line-height: 1;
}
</style>
