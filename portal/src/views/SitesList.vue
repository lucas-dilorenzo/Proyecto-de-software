<template>
  <main class="container py-3">
    <!-- Header con título y filtro -->
    <header class="d-flex justify-content-between align-items-baseline gap-3 mb-3">
      <h1 class="m-0">Listado de Sitios</h1>
      <select
        v-model="orderBy"
        @change="reload()"
        class="form-select form-select-sm"
        style="width: auto"
      >
        <option value="latest">Recientes</option>
        <option value="rating-5-1">Mejor puntuados</option>
        <option value="rating-1-5">Peor puntuados</option>
        <option value="oldest">Más antiguos</option>
      </select>
    </header>

    <section>
      <!-- Error -->
      <div v-if="error" class="alert alert-danger" role="alert">Error: {{ error }}</div>

      <!-- Loading -->
      <div v-else-if="loading" class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-3">
        <div class="col" v-for="i in 8" :key="i">
          <SkeletonCard />
        </div>
      </div>

      <!-- No results -->
      <div v-else-if="items.length === 0" class="text-center text-muted py-5">
        No hay resultados
      </div>

      <!-- Results grid -->
      <div v-else class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-3">
        <div class="col" v-for="s in items" :key="s.id">
          <SiteCard :site="s" @open="openDetail" />
        </div>
      </div>

      <!-- Load more button -->
      <div v-if="!loading && hasMore" class="d-flex justify-content-center mt-4">
        <button class="btn btn-outline-primary" @click="loadMore">Cargar más</button>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { type Site } from '@/services/api'
import { logger } from '@/utils/logger' // 🔹 Importar logger
import SkeletonCard from '@/components/SkeletonCard.vue'
import SiteCard from '@/components/SiteCard.vue'

const route = useRoute()
const router = useRouter()

const orderBy = ref<string>((route.query.order_by as string) || 'latest')
const q = ref<string>((route.query.q as string) || '')

const page = ref(1)
const pageSize = 12
const items = ref<Site[]>([])
const loading = ref(false)
const error = ref('')
const hasMore = ref(true)

function syncUrl() {
  const query: Record<string, string> = {}
  if (orderBy.value) query.order_by = orderBy.value
  if (q.value) query.q = q.value
  router.replace({ name: 'sites-list', query })
}

async function fetchPage(p: number) {
  loading.value = true
  error.value = ''
  try {
    logger.log('📦 SitesList fetchPage:', p, orderBy.value) // 🔹 Usar logger

    const res = await api.getSitesApi().list({
      order_by: orderBy.value as any,
      page: p,
      per_page: pageSize,
    })

    const pageItems = res.data ?? []
    if (p === 1) items.value = pageItems
    else items.value = [...items.value, ...pageItems]

    hasMore.value = p * res.meta.per_page < res.meta.total

    logger.log('✅ SitesList loaded:', pageItems.length, 'items') // 🔹 Usar logger
  } catch (e: any) {
    logger.error('❌ SitesList error:', e) // 🔹 Usar logger
    error.value = e?.message || 'Error al cargar'
  } finally {
    loading.value = false
  }
}

function reload() {
  syncUrl()
  page.value = 1
  fetchPage(1)
}

function loadMore() {
  if (!hasMore.value) return
  page.value += 1
  fetchPage(page.value)
}

function openDetail(site: Site) {
  router.push({ name: 'site-detail', params: { id: site.id } })
}

watch(
  () => route.query,
  () => {
    orderBy.value = (route.query.order_by as string) || 'latest'
    q.value = (route.query.q as string) || ''
    reload()
  },
)

onMounted(() => {
  logger.log('✅ SitesList mounted') // 🔹 Usar logger
  reload()
})
</script>

<style scoped>
/* Sin estilos custom necesarios */
</style>
