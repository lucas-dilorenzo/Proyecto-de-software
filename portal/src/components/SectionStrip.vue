<template>
  <section ref="rootEl" class="my-4">
    <header class="d-flex justify-content-between align-items-baseline mb-3">
      <h2 class="h4 mb-0" style="font-family: 'Playfair Display', serif">{{ title }}</h2>
      <button class="btn btn-link text-decoration-none p-0" @click="goSeeAll">Ver todos ›</button>
    </header>

    <div v-if="error" class="alert alert-danger" role="alert">Error: {{ error }}</div>

    <div v-else>
      <div v-if="loading" class="row row-cols-2 row-cols-md-3 row-cols-lg-4 g-3">
        <div class="col" v-for="i in 6" :key="i">
          <SkeletonCard />
        </div>
      </div>

      <div v-else-if="items.length === 0" class="text-center py-3">
        <span class="badge rounded-pill bg-light text-muted border px-3 py-2">
          No hay contenido
        </span>
      </div>

      <div v-else class="row row-cols-2 row-cols-md-3 row-cols-lg-4 g-3">
        <div class="col" v-for="s in items" :key="s.id">
          <SiteCard :site="s" @open="openDetail" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import SkeletonCard from './SkeletonCard.vue'
import SiteCard from './SiteCard.vue'
import { SitesAPI, type Site } from '@/services/api'
import { logger } from '@/utils/logger'

const props = defineProps<{
  title: string
  /** 'visited' | 'rating' | 'recent' | 'favorites' */
  sort: string
  seeAllQuery?: Record<string, string | number | boolean>
  authRequired?: boolean
}>()

const router = useRouter()
const items = ref<Site[]>([])
const loading = ref(false)
const error = ref('')
const rootEl = ref<HTMLElement | null>(null)
let observer: IntersectionObserver | null = null

function goSeeAll() {
  router.push({ name: 'sites-list', query: { order_by: props.sort } })
}

function openDetail(site: Site) {
  router.push({ name: 'site-detail', params: { id: site.id } })
}

async function fetchData() {
  try {
    loading.value = true
    error.value = ''
    logger.log('📦 SectionStrip fetch:', props.title, props.sort)

    if (props.sort === 'favorites') {
      const res = await SitesAPI.favorites({ page: 1, per_page: 12 })
      logger.log('✅ API /me/favorites:', res)
      items.value = res.data || []
    } else {
      const res = await SitesAPI.list({ order_by: props.sort as any, per_page: 12 })
      logger.log('✅ API /sites:', res)
      items.value = res.data || []
    }
  } catch (e: any) {
    logger.error('❌ SectionStrip error:', e)
    error.value = e?.message || 'Error al cargar'
  } finally {
    loading.value = false
  }
}

function makeLazy() {
  if (!('IntersectionObserver' in window)) {
    fetchData()
    return
  }
  observer = new IntersectionObserver(
    (entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        fetchData()
        observer?.disconnect()
      }
    },
    { rootMargin: '200px' },
  )
  if (rootEl.value) observer.observe(rootEl.value)
}

onMounted(makeLazy)
onBeforeUnmount(() => observer?.disconnect())
</script>

<style scoped>
/* Único estilo que Bootstrap no cubre: fuente custom del título */
</style>
