<template>
  <main class="container" style="padding-top: 16px">
    <header
      style="
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 16px;
      "
    >
      <h1 style="margin: 0">Listado de Sitios</h1>
      <select v-model="orderBy" @change="reload()" class="select">
        <option value="latest">Recientes</option>
        <option value="rating-5-1">Mejor puntuados</option>
        <option value="rating-1-5">Peor puntuados</option>
        <option value="oldest">Más antiguos</option>
      </select>
    </header>

    <section>
      <div v-if="error" class="subtle">Error: {{ error }}</div>

      <div v-else-if="loading" class="grid">
        <SkeletonCard v-for="i in 8" :key="i" />
      </div>

      <div v-else-if="items.length === 0" class="subtle" style="text-align: center">
        No hay resultados
      </div>

      <div v-else class="grid">
        <SiteCard v-for="s in items" :key="s.id" :site="s" @open="openDetail" />
      </div>

      <div
        v-if="!loading && hasMore"
        style="display: flex; justify-content: center; margin-top: 16px"
      >
        <button class="btn" @click="loadMore">Cargar más</button>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { SitesAPI, type Site } from '@/services/api'
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
    const res = await SitesAPI.list({
      order_by: orderBy.value as any, // 'latest' | 'rating-5-1' | ...
      page: p,
      per_page: pageSize,
      // name: q.value || undefined,  // si tu API soporta búsqueda por nombre
    })
    const pageItems = res.data ?? []
    if (p === 1) items.value = pageItems
    else items.value = [...items.value, ...pageItems]

    // hasMore con total oficial:
    hasMore.value = p * res.per_page < res.total
  } catch (e: any) {
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

onMounted(() => reload())
</script>
