<template>
  <main class="container-fluid d-flex align-items-center justify-content-center min-vh-100 px-3">
    <div class="text-center" style="max-width: 600px;">
      <div class="card border-0 shadow-sm p-4 p-md-5">
        <!-- Icono de mantenimiento -->
        <div class="mb-4">
          <div class="maintenance-icon-wrapper mx-auto mb-3">
            <i class="bi bi-tools" style="font-size: 4rem; color: var(--brand);"></i>
          </div>
          <h1 class="h1 mb-3" style="font-family: 'Playfair Display', serif;">
            Estamos en mantenimiento
          </h1>
        </div>

        <!-- Mensaje principal -->
        <div class="mb-4">
          <p class="lead text-muted mb-3">
            Actualmente estamos realizando tareas de mantenimiento para mejorar tu experiencia.
          </p>
          <p class="text-muted">
            Por favor, vuelve a intentarlo en unos momentos. Agradecemos tu paciencia.
          </p>
        </div>

        <!-- Información adicional -->
        <div class="alert alert-light border py-3 mb-4">
          <div class="d-flex align-items-center justify-content-center gap-2">
            <i class="bi bi-clock" style="color: var(--brand);"></i>
            <span class="small text-muted">
              Tiempo estimado: <strong>{{ estimatedTime }}</strong>
            </span>
          </div>
        </div>

        <!-- Botón de recarga -->
        <div class="d-grid gap-2">
          <button 
            class="btn btn-primary btn-lg" 
            @click="checkStatus"
            :disabled="isChecking"
          >
            <span v-if="!isChecking">
              <i class="bi bi-arrow-clockwise me-2"></i>
              Verificar estado
            </span>
            <span v-else>
              <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Verificando...
            </span>
          </button>
          
          <a href="/" class="btn btn-outline-secondary">
            <i class="bi bi-house-door me-2"></i>
            Volver al inicio
          </a>
        </div>

        <!-- Contador de intentos automáticos -->
        <div class="mt-4" v-if="autoCheckEnabled">
          <small class="text-muted">
            <i class="bi bi-arrow-repeat"></i>
            Próxima verificación automática en {{ countdown }}s
          </small>
        </div>
      </div>

      <!-- Footer -->
      <footer class="mt-4">
        <nav class="d-flex justify-content-center gap-3 flex-wrap">
          <a href="#" class="text-muted text-decoration-none small">Términos</a>
          <a href="#" class="text-muted text-decoration-none small">Privacidad</a>
          <a href="#" class="text-muted text-decoration-none small">Contacto</a>
        </nav>
      </footer>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const isChecking = ref(false)
const estimatedTime = ref('Unos minutos')
const autoCheckEnabled = ref(true)
const countdown = ref(30)
let countdownInterval: number | null = null
let autoCheckInterval: number | null = null

const checkStatus = async () => {
  isChecking.value = true
  try {
    const response = await api.getFlagsApi().getStatus()
    if (!response.data.maintenance_mode) {
      // Si ya no está en mantenimiento, redirigir al inicio
      router.push('/')
    }
  } catch (error) {
    console.error('Error al verificar el estado:', error)
  } finally {
    isChecking.value = false
  }
}

const startCountdown = () => {
  countdown.value = 30
  countdownInterval = window.setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      countdown.value = 30
    }
  }, 1000)
}

const startAutoCheck = () => {
  autoCheckInterval = window.setInterval(async () => {
    await checkStatus()
  }, 30000) // Verificar cada 30 segundos
}

onMounted(() => {
  startCountdown()
  startAutoCheck()
})

onUnmounted(() => {
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
  if (autoCheckInterval) {
    clearInterval(autoCheckInterval)
  }
})
</script>

<style scoped>
.maintenance-icon-wrapper {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(47, 165, 115, 0.1), rgba(47, 165, 115, 0.05));
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background: var(--brand);
  border-color: var(--brand);
}

.btn-primary:hover {
  background: #268862;
  border-color: #268862;
}

.btn-primary:disabled {
  background: #8b8f97;
  border-color: #8b8f97;
}

.alert-light {
  background-color: rgba(47, 165, 115, 0.05);
}
</style>
