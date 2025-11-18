<template>
  <AuthProvider>
    <div>
      <header class="topbar">
        <div class="col d-flex justify-content-between align-items-center">
          <div class="col-md-1">
            <router-link to="/" class="navbar-brand"> Portal Público </router-link>
          </div>
          <div class="col-md-10"></div>
          <div class="col-md-1">
            <div v-if="isLoggedIn">
              <UserDropdown :loggedIn="isLoggedIn" />
            </div>
            <router-link v-else to="/login">Log In</router-link>
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
</style>
