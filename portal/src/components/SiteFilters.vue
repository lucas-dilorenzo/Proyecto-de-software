<template>
  <div class="site-filters bg-light">
    <div class="accordion" id="accordionFilters">
      <div class="accordion-item border-0">
        <h2 class="accordion-header">
          <button
            class="accordion-button collapsed"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#collapseFilters"
            aria-expanded="false"
            aria-controls="collapseFilters"
          >
            <i class="bi bi-funnel me-2"></i>
            Filtros Avanzados
          </button>
        </h2>
        <div
          id="collapseFilters"
          class="accordion-collapse collapse"
          data-bs-parent="#accordionFilters"
        >
          <div class="accordion-body">
            <form @submit.prevent="applyFilters" class="row g-3">
              <!-- Ciudad -->
              <div class="col-md-6">
                <label for="filter-city" class="form-label">
                  <i class="bi bi-geo-alt me-1"></i>Ciudad
                </label>
                <input
                  id="filter-city"
                  v-model="filters.city"
                  type="text"
                  class="form-control"
                  placeholder="Ingrese una ciudad"
                />
              </div>

              <!-- Provincia -->
              <div class="col-md-6">
                <label class="form-label">
                  <i class="bi bi-map me-1"></i>Provincia
                </label>
                <div class="dropdown">
                  <button
                    class="btn btn-outline-secondary dropdown-toggle w-100 text-start"
                    type="button"
                    data-bs-toggle="dropdown"
                    data-bs-auto-close="true"
                    aria-expanded="false"
                  >
                    {{ filters.province || 'Todas las provincias' }}
                  </button>
                  <ul class="dropdown-menu w-100" style="max-height: 300px; overflow-y: auto;">
                    <li>
                      <a
                        class="dropdown-item"
                        :class="{ active: !filters.province }"
                        href="#"
                        @click.prevent="filters.province = ''"
                      >
                        Todas las provincias
                      </a>
                    </li>
                    <li><hr class="dropdown-divider" /></li>
                    <li v-for="province in provinces" :key="province">
                      <a
                        class="dropdown-item"
                        :class="{ active: filters.province === province }"
                        href="#"
                        @click.prevent="filters.province = province"
                      >
                        {{ province }}
                      </a>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Tags -->
              <div class="col-md-6">
                <label class="form-label">
                  <i class="bi bi-tags me-1"></i>Tags
                </label>
                <div class="border rounded p-2 bg-white" style="max-height: 200px; overflow-y: auto;">
                  <div
                    v-for="tag in tags"
                    :key="tag"
                    class="form-check mb-2"
                  >
                    <input
                      :id="`tag-${tag}`"
                      v-model="filters.tags"
                      type="checkbox"
                      class="form-check-input"
                      :value="tag"
                    />
                    <label :for="`tag-${tag}`" class="form-check-label user-select-none">
                      {{ tag }}
                    </label>
                  </div>
                </div>
              </div>

              <!-- Favoritos -->
              <!-- TODO: Implementar filtro de favoritos en el backend -->
              <!-- <div class="col-md-6">
                <label class="form-label d-block">
                  <i class="bi bi-star me-1"></i>Opciones
                </label>
                <div class="form-check">
                  <input
                    id="filter-favorites"
                    v-model="filters.onlyFavorites"
                    type="checkbox"
                    class="form-check-input"
                  />
                  <label for="filter-favorites" class="form-check-label">
                    Solo mostrar mis favoritos
                  </label>
                </div>
              </div> -->

              <!-- Botones de acción -->
              <div class="col-12">
                <div class="d-flex gap-2 justify-content-end">
                  <button
                    type="button"
                    @click="clearFilters"
                    class="btn btn-outline-secondary"
                  >
                    <i class="bi bi-x-circle me-1"></i>Limpiar
                  </button>
                  <button type="submit" class="btn btn-primary">
                    <i class="bi bi-search me-1"></i>Aplicar Filtros
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'
import { logger } from '@/utils/logger'

interface Filters {
  city: string
  province: string
  tags: string[]
  onlyFavorites: boolean
}

const router = useRouter()
const route = useRoute()

// Estado de los filtros
const filters = ref<Filters>({
  city: '',
  province: '',
  tags: [],
  onlyFavorites: false
})

// Datos para los selectores
const provinces = ref<string[]>([])
// Cargar provincias desde la API

const tags = ref<string[]>([])

// Cargar tags disponibles desde la API
onMounted(async () => {
  // TODO: Implementar llamada a la API para obtener tags
  const tagsResponse = await api.getTagsApi().list()
  tags.value = tagsResponse.data.map(tag => tag.name)
  
  const provincesResponse = await api.getSitesApi().listProvinces()
  logger.log('Provincias cargadas:', provincesResponse)
  provinces.value = provincesResponse.data

  // Cargar filtros desde la URL si existen
  loadFiltersFromQuery()
})

// Cargar filtros desde la query string
function loadFiltersFromQuery() {
  const query = route.query  

  if (query.city) {
    filters.value.city = query.city as string
  }
  if (query.province) {
    filters.value.province = query.province as string
  }
  if (query.tags) {
    const tagsParam = query.tags as string
    filters.value.tags = tagsParam.split(',').filter(t => t.trim())
  }
  // TODO: Implementar filtro de favoritos en el backend
  // if (query.favorites === 'true') {
  //   filters.value.onlyFavorites = true
  // }
}

// Aplicar filtros
function applyFilters() {
  const query: Record<string, string> = {}

  if (filters.value.city.trim()) {
    query.city = filters.value.city.trim()
  }
  if (filters.value.province) {
    query.province = filters.value.province
  }
  if (filters.value.tags.length > 0) {
    query.tags = filters.value.tags.join(',')
  }
  // TODO: Implementar filtro de favoritos en el backend
  // if (filters.value.onlyFavorites) {
  //   query.favorites = 'true'
  // }

  // Mantener la búsqueda de texto si existe
  if (route.query.q) {
    query.q = route.query.q as string
  }

  router.push({ name: 'sites-list', query })
}

// Limpiar filtros
function clearFilters() {
  filters.value = {
    city: '',
    province: '',
    tags: [],
    onlyFavorites: false
  }

  // Si hay una búsqueda de texto, mantenerla
  const query: Record<string, string> = {}
  if (route.query.q) {
    query.q = route.query.q as string
  }

  router.push({ name: 'sites-list', query })
}
</script>


