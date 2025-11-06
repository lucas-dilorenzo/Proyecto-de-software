<template>
  <section ref="rootEl" class="section">
    <header class="section-header">
      <h2>{{ title }}</h2>
      <button class="btn-link" @click="goSeeAll">Ver todos ›</button>
    </header>

    <div v-if="error" class="empty subtle">Error: {{ error }}</div>

    <div v-else>
      <div v-if="loading" class="grid">
        <SkeletonCard v-for="i in 6" :key="i" />
      </div>

      <div v-else-if="items.length === 0" class="empty subtle pill">No hay contenido</div>

      <div v-else class="grid">
        <SiteCard v-for="s in items" :key="s.id" :site="s" @open="openDetail" />
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
  // Convertir booleanos a strings
  const query = Object.entries(props.seeAllQuery || {}).reduce(
    (acc, [key, value]) => {
      acc[key] = typeof value === 'boolean' ? (value ? '1' : '0') : value
      return acc
    },
    {} as Record<string, string | number>,
  )

  router.push({ name: 'sites-list', query })
}
function openDetail(site: Site) {
  router.push({ name: 'site-detail', params: { id: site.id } })
}

async function fetchData() {
  try {
    loading.value = true
    error.value = ''
    if (props.sort === 'favorites') {
      const res = await SitesAPI.favorites({ limit: 12 })
      items.value = res.items || []
    } else {
      const res = await SitesAPI.list({ sort: props.sort as any, limit: 12 })
      items.value = res.items || []
    }
  } catch (e: any) {
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
.section {
  margin: 24px 0;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 16px;
}
.section-header h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.4rem;
  margin: 0;
}
.btn-link {
  background: none;
  border: none;
  color: var(--fg);
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: color 0.2s;
}
.btn-link:hover {
  color: var(--brand);
}

.grid {
  display: grid;
  gap: 18px;
}
@media (max-width: 767px) {
  .grid {
    grid-template-columns: 1fr 1fr;
  }
}
@media (min-width: 768px) and (max-width: 1024px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (min-width: 1025px) {
  .grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.empty {
  text-align: center;
}
.pill {
  display: inline-block;
  margin: 8px auto 0;
  padding: 10px 16px;
  border: 1px solid #e0dbd3;
  border-radius: 999px;
  background: #fff;
}
</style>
