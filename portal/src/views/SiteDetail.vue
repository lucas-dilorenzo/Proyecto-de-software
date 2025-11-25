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
          <div class="d-flex align-items-center text-muted">
            <!-- Mostrar estrellas basadas en el promedio de calificaciones -->
            <div v-if="promedioEstrellasCalificaciones !== null" class="d-flex align-items-center">
              <div class="me-2">
                <i 
                  v-for="star in 5" 
                  :key="star"
                  class="bi me-1"
                  :class="star <= Math.round(promedioEstrellasCalificaciones) ? 'bi-star-fill text-warning' : 'bi-star text-muted'"
                ></i>
              </div>
              <span>{{ promedioEstrellasCalificaciones.toFixed(1) }} ({{ totalReviewsCount }} reseñas)</span>
            </div>
            <span v-else>
              <i class="bi bi-star text-muted me-1"></i>
              Sin calificaciones
            </span>
          </div>
        </div>

        <div class="mb-3">
          <h5>Descripción</h5>
          <p>{{ site.description || 'Sin descripción disponible' }}</p>
        </div>

        <div v-if="site.tags && site.tags.length > 0" class="mb-3">
          <h5>Etiquetas</h5>
          <div class="d-flex flex-wrap gap-2">
            <button 
              v-for="tag in site.tags" 
              :key="tag" 
              @click="filterByTag(tag)"
              class="badge bg-secondary text-decoration-none border-0 clickable-tag"
              :title="`Ver todos los sitios con etiqueta: ${tag}`"
            >
              {{ tag }}
            </button>
          </div>
        </div>

        <div class="d-flex gap-2">
          <button @click="router.back()" class="btn btn-outline-secondary">Volver</button>          
          <div v-if="esta_logeado">
            <button v-if="es_favorito" @click="eliminar_favorito()" class="btn btn-primary" >Eliminar de favoritos</button>
            <button v-else @click="agregar_favorito()" class="btn btn-outline-primary">Agregar a favoritos</button>
          </div>
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
                <p>{{ site.conservation_status || 'No especificado' }}</p>
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
      <section class="col-12 reviews-section">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title mb-4">Reseñas</h5>
            <div v-if="esta_logeado">
              <!-- Si estoy logueado y tengo una reseña sobre este sitio -->
              <div v-if="myReview" class="card">
                <div class="card-body">
                  <div class="card-title">
                    <h6>Mi reseña:</h6>
                  </div>
                  <ListReviews 
                    :review="[myReview]"
                    :current-user-review-id="myReview.id"
                    @update-review="handleUpdateReview"
                    @delete-review="handleDeleteReview"
                  />
                </div>
              </div>
              <!-- Componente para agregar una nueva reseña -->
              <div v-else class="mt-4">
                <NewReview :siteId="site?.id" />
              </div>
            </div>
            <div v-else class="alert alert-info mt-4">
              Inicie sesión para agregar una reseña.
            </div>
            <!-- Mostrar Primero las reseñas del usuario logueado -->
            <!-- Componente para mostrar las reseñas -->
            <ListReviews :review="reviews || []"/>            
          </div>
        </div>
      </section>
    </article>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { type Site, Review } from '@/services/api'
import { logger } from '@/utils/logger'
import MapComponent from '@/components/MapComponent.vue'
import { useAuthStore } from '@/stores/auth'
import ListReviews from '@/components/ListReviews.vue'
import NewReview from '@/components/NewReview.vue'

const route = useRoute()
const router = useRouter()

const id = Number(route.params.id)
const site = ref<Site | null>(null)
const closeSites = ref<Site[]>([])
const loading = ref(false)
const error = ref('')
const radius = ref(50)
const reviews = ref<Review[] | null>(null)
const myReviews = ref<Review[]>([])
const myReview = ref<Review>()
const esta_logeado = computed(() => {
  return useAuthStore().isLoggedIn
});
const es_favorito = ref(false)

// Cálculo del promedio de calificaciones basado en las reseñas aprobadas
const promedioEstrellasCalificaciones = computed(() => {
  const allReviews = []
  
  if (myReview.value) {
    allReviews.push(myReview.value)
  }
  if (reviews.value) {
    allReviews.push(...reviews.value)
  }
  
  if (allReviews.length === 0) return null
  
  // Calcular promedio de calificaciones
  const totalPromedio = allReviews.reduce((sum, review) => sum + (review.rating || 0), 0)
  return totalPromedio / allReviews.length
})

const totalReviewsCount = computed(() => {
  let count = 0
  if (myReview.value) count++
  if (reviews.value) count += reviews.value.length
  return count
})

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

onMounted(async() => {
  logger.log('✅ SiteDetail mounted, id:', id)
  await await fetchSite()
  await fetchCloseSites()
  await comprobar_fav()
  await fetchReviews()
  if(esta_logeado.value){
    await fetchMyReviewsOnSite()
    await filterReviews()
  }
})

async function comprobar_fav(){
  if(esta_logeado.value == true){
    try{
      const listado_favoritos = await api.getUserApi().getFavorites({}, '') //revisar esto (argumentos de getFavorites)
      es_favorito.value = listado_favoritos.data.some(
        (fav_site: Site) => fav_site.id === site.value?.id
      )
    } catch (e: unknown) {
      const err = e instanceof Error ? e : new Error(String(e))
      logger.error('Error al comprobar favoritos:', err)
      return false
    }
  }  
}

async function agregar_favorito(){
  try {

    await api.getSitesApi().star(site.value!.id, '')
    es_favorito.value = true

    alert('Sitio agregado a favoritos')
  } catch (e: unknown) {
    const err = e instanceof Error ? e : new Error(String(e))
    logger.error('Error:', err)
    alert('Error: ' + err.message)
  }
}

async function eliminar_favorito(){
  try {
    
    await api.getSitesApi().unstar(site.value!.id, '')
    es_favorito.value = false

    alert('Sitio eliminado de favoritos')
  } catch (e: unknown) {
    const err = e instanceof Error ? e : new Error(String(e))
    logger.error('Error:', err)
    alert('Error: ' + err.message)
  }
}

async function fetchReviews() {
  if (!site.value) return

  try {
    logger.log('📦 SiteDetail fetching reviews for site:', site.value.id)

    const data = await api.getSiteReviewsApi(site.value.id).list()

    reviews.value = data.data
    logger.log('✅ SiteDetail loaded reviews:', reviews.value.length)
  } catch (e: unknown) {
    const err = e instanceof Error ? e : new Error(String(e))
    logger.error('❌ SiteDetail error fetching reviews:', err)
    reviews.value = null
  }
}

async function fetchMyReviewsOnSite() {
  try {
    const response = await api.getUserApi().getReviews('')
    myReviews.value = response.data
    if(myReviews.value.length > 0){
      myReview.value = myReviews.value.filter((review) => review.site_id === site.value?.id)[0]
      console.log('Mi reseña:', myReview.value)
    } else {
      console.log('Reseñas del usuario(debería tener una sola):', myReviews)
    }
  } catch (error) {
    console.error('Error al obtener mis reseñas:', error)
  }
}

async function filterReviews() {
  if (reviews.value && myReview.value) {
    reviews.value = reviews.value.filter((review) => review.id !== myReview.value!.id)
    console.log('Reseñas filtradas (sin la del usuario):', reviews.value)
  }
}

async function handleUpdateReview(reviewId: number, rating: number, comment: string) {
  if (!site.value) return

  try {
    logger.log('📝 Actualizando reseña:', { reviewId, rating, comment })
    
    // Llamar a la API para actualizar la reseña
    await api.getSiteReviewsApi(site.value.id).update(reviewId, { 
      rating, 
      comment 
    }, '')

    // Actualizar la reseña localmente si es la del usuario actual
    if (myReview.value && myReview.value.id === reviewId) {
      myReview.value = {
        ...myReview.value,
        rating,
        comment,
        updated_at: new Date()
      }
    }

    alert('Reseña actualizada exitosamente')
    await fetchSite() // Actualizar el rating promedio del sitio
  } catch (e: unknown) {
    const err = e instanceof Error ? e : new Error(String(e))
    logger.error('❌ Error al actualizar reseña:', err)
    alert('Error al actualizar la reseña: ' + err.message)
  }
}

async function handleDeleteReview(reviewId: number) {
  if (!site.value) return

  try {
    logger.log('🗑️ Eliminando reseña:', reviewId)
    
    await api.getSiteReviewsApi(site.value.id).delete(reviewId, '')

    // Limpiar la reseña del usuario
    myReview.value = undefined

    alert('Reseña eliminada exitosamente')
    await fetchSite() // Actualizar el rating promedio del sitio
  } catch (e: unknown) {
    const err = e instanceof Error ? e : new Error(String(e))
    logger.error('❌ Error al eliminar reseña:', err)
    alert('Error al eliminar la reseña: ' + err.message)
  }
}

// Función para filtrar sitios por tag al clickearlo
function filterByTag(tag: string) {
  logger.log('🏷️ Filtering by tag:', tag)
  router.push({ 
    
    name: 'sites-list', 
    query: { 
      tags: tag.toLowerCase()  
    } 
  })
}

</script>

<style scoped>
.clickable-tag {
  cursor: pointer;
  transition: all 0.2s ease;
}

.clickable-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background-color: #495057 !important;
}

.clickable-tag:active {
  transform: translateY(0);
}
</style>
