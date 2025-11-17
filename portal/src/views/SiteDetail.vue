<template>
  <main class="container py-4">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      <strong>Error:</strong> {{ error }}
      <button @click="router.back()" class="btn btn-sm btn-outline-danger ms-3">Volver</button>
    </div>

    <article v-else-if="site" class="row g-4">
      <section class="col-12 col-lg-6">
        <div
          v-if="site.images && site.images.length > 0"
          id="carouselImages"
          class="carousel slide"
        >
          <div class="carousel-inner rounded">
            <div
              v-for="(img, idx) in site.images"
              :key="img.id"
              class="carousel-item"
              :class="{ active: idx === 0 }"
            >
              <img
                :src="img.url"
                class="d-block w-100"
                :alt="site.name"
                style="max-height: 400px; object-fit: cover"
              />
            </div>
          </div>
          <button
            class="carousel-control-prev"
            type="button"
            data-bs-target="#carouselImages"
            data-bs-slide="prev"
          >
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Anterior</span>
          </button>
          <button
            class="carousel-control-next"
            type="button"
            data-bs-target="#carouselImages"
            data-bs-slide="next"
          >
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Siguiente</span>
          </button>
        </div>
        <div
          v-else
          class="bg-light rounded d-flex align-items-center justify-content-center"
          style="height: 400px"
        >
          <p class="text-muted">Sin imágenes</p>
        </div>
      </section>

      <section class="col-12 col-lg-6">
        <div class="mb-3">
          <h1 class="mb-2">{{ site.name }}</h1>
          <p class="text-muted mb-1">
            <i class="bi bi-geo-alt"></i>
            {{ site.city }}, {{ site.province }}
          </p>
          <p class="text-muted">
            <i class="bi bi-star-fill text-warning"></i>
            {{ site.avg_rating ?? 'Sin calificación' }}
          </p>
        </div>

        <div class="mb-3">
          <h5>Descripción</h5>
          <p>{{ site.description || 'Sin descripción disponible' }}</p>
        </div>

        <div v-if="site.tags && site.tags.length > 0" class="mb-3">
          <h5>Etiquetas</h5>
          <div class="d-flex flex-wrap gap-2">
            <span v-for="tag in site.tags" :key="tag" class="badge bg-secondary">
              {{ tag }}
            </span>
          </div>
        </div>

        <div class="d-flex gap-2">
          <button @click="router.back()" class="btn btn-outline-secondary">Volver</button>
          <!-- <button class="btn btn-primary">Ver en mapa</button> -->
        </div>
      </section>

      <!-- Additional Info -->
      <section class="col-12">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Información adicional</h5>
            <div class="row g-3">
              <div class="col-md-6">
                <strong>Coordenadas:</strong>
                <p>{{ site.latitude }}, {{ site.longitude }}</p>
              </div>
              <div class="col-md-6">
                <strong>Estado de conservación:</strong>
                <p>{{ site.state_of_conservation || 'No especificado' }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section class="col-12 ubication-section">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Ubicación</h5>
            <!-- mapa de leafleat -->
            <!-- si no hay sitios cercanos usar este componente -->
            <MapComponent v-if="closeSites.length === 0" :lat="site.latitude" :lng="site.longitude" :zoom="12"/>
            <!-- si hay sitios cercanos usar este componente -->
            <MapComponent v-else :lat="site.latitude" :lng="site.longitude" :closeSites="closeSites" :radius="radius" />
          </div>
        </div>
      </section>
    </article>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { type Site } from '@/services/api'
import { logger } from '@/utils/logger'
import MapComponent from '@/components/MapComponent.vue'

const route = useRoute()
const router = useRouter()

const id = Number(route.params.id)
const site = ref<Site | null>(null)
const closeSites = ref<Site[]>([])
const loading = ref(false)
const error = ref('')
const radius = ref(50)

async function fetchSite() {
  loading.value = true
  error.value = ''

  try {
    logger.log('📦 SiteDetail fetching site:', id)

    const data = await api.getSitesApi().get(id)
    site.value = data

    logger.log('✅ SiteDetail loaded:', data)
  } catch (e: unknown) {
    const err = e instanceof Error ? e : new Error(String(e))
    logger.error('❌ SiteDetail error:', err)
    error.value = err.message || 'Error al cargar el sitio'
  } finally {
    loading.value = false
  }
}

async function fetchCloseSites() {
  if (!site.value) return

  try {
    logger.log('📦 SiteDetail fetching close sites for site:', site.value.id)

    const data = await api.getSitesApi().list({
      lat: site.value.latitude,
      long: site.value.longitude,
      radius: radius.value,
    })

    closeSites.value = data.data.filter((s: Site) => s.id !== site.value?.id)
    logger.log('✅ SiteDetail loaded close sites:', closeSites.value.length)
  } catch (e: unknown) {
    const err = e instanceof Error ? e : new Error(String(e))
    logger.error('❌ SiteDetail error fetching close sites:', err)
    closeSites.value = []
  }
}

onMounted(async () => {
  logger.log('✅ SiteDetail mounted, id:', id)
  await fetchSite()
  await fetchCloseSites()
})
</script>

<style scoped></style>
