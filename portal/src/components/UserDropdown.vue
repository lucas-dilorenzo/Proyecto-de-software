<template>
  <div v-if="props.loggedIn" class="dropdown">
    <button
      class="btn btn-sm btn-outline-secondary dropdown-toggle d-flex align-items-center gap-2"
      type="button"
      id="userDropdown"
      data-bs-toggle="dropdown"
      data-bs-offset="0,4"
      aria-label="Cuenta de usuario"
      aria-expanded="false"
      :title="displayName"
    >
      <img
        :src="avatarSrc"
        :alt="`Avatar de ${displayName}`"
        width="34"
        height="34"
        class="rounded-circle border"
      />
      <span class="d-none d-md-inline text-truncate" style="max-width: 120px">{{ displayName }}</span>
    </button>

    <ul class="dropdown-menu dropdown-menu-end text-small shadow" aria-labelledby="userDropdown">
      <li class="px-3 py-2">
        <div class="d-flex align-items-center">
          <img :src="avatarSrc" alt="avatar" width="40" height="40" class="rounded-circle border me-2" />
          <div>
            <div class="fw-bold">{{ displayName }}</div>
            <div class="text-muted small">{{ email }}</div>
          </div>
        </div>
      </li>
      <li><hr class="dropdown-divider" /></li>
      <li>
        <router-link to="/profile" class="dropdown-item d-flex align-items-center">
          <i class="bi bi-person me-2"></i>
          Perfil
        </router-link>
      </li>
      <li>
        <router-link to="/settings" class="dropdown-item d-flex align-items-center">
          <i class="bi bi-gear me-2"></i>
          Configuración
        </router-link>
      </li>
      <li>
        <hr class="dropdown-divider" />
      </li>
      <li>
        <button class="dropdown-item d-flex align-items-center text-danger" @click.prevent="logout">
          <i class="bi bi-box-arrow-right me-2"></i>
          Cerrar sesión
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { computed } from 'vue'

const props = defineProps({
  loggedIn: { type: Boolean, required: true },
})

const authStore = useAuthStore()
const router = useRouter()

const logout = async () => {
  await authStore.logoutUser()
  router.push('/login')
}

const displayName = computed(() => authStore.user?.usuario || authStore.user?.email || 'Usuario')
const email = computed(() => authStore.user?.email || '')
const avatarSrc = computed(() => 'https://api.iconify.design/bi/person-fill.svg')
</script>

<style scoped>
.dropdown .btn .rounded-circle {
  width: 34px;
  height: 34px;
  object-fit: cover;
}

.dropdown .dropdown-menu {
  min-width: 220px;
  max-width: 320px;
}

.dropdown .dropdown-item .bi {
  font-size: 1rem;
}

.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
