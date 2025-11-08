<template>
  <section class="card border-0 shadow-sm mb-4">
    <div class="card-body py-4 py-md-5 px-3 px-md-4">
      <div class="text-center mx-auto" style="max-width: 880px;">
        <h1 class="display-5 fw-bold mb-2">Sitios Históricos</h1>
        <p class="text-muted mb-4">Descubrí lugares destacados y experiencias cerca tuyo.</p>
        
        <form @submit.prevent="goSearch" class="d-flex gap-2 justify-content-center">
          <input 
            v-model.trim="q" 
            type="search" 
            placeholder="Buscar sitios…" 
            class="form-control form-control-lg"
            style="max-width: 640px;"
          />
          <button type="submit" class="btn btn-primary btn-lg">
            Buscar
          </button>
        </form>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { logger } from '@/utils/logger'

const q = ref('')
const router = useRouter()

function goSearch() {
  if (!q.value.trim()) return
  
  logger.log('🔍 HeroSearch: searching for', q.value)
  router.push({ name: 'sites-list', query: { q: q.value } })
}
</script>

<style scoped>
/* Estilos mínimos, Bootstrap maneja el resto */
</style>
