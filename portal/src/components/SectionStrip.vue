<template>
  <section ref="rootEl" class="section">
    <header class="section-header">
      <h2>{{ title }}</h2>
      <button class="see-all" @click="goSeeAll">Ver todos</button>
    </header>

    <div v-if="error" class="empty">Error: {{ error }}</div>

    <div v-else class="content">
      <div v-if="loading" class="grid">
        <SkeletonCard v-for="i in 6" :key="i" />
      </div>
      <div v-else-if="items.length === 0" class="empty">No hay elementos para mostrar.</div>
      <div v-else class="grid">
        <SiteCard v-for="s in items" :key="s.id" :site="s" @open="openDetail" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import SkeletonCard from './SkeletonCard.vue'
import SiteCard from './SiteCard.vue'
import { SitesAPI } from '@/services/api'
import { useRouter } from 'vue-router'

const props = defineProps({
  title: { type: String, required: true },
  // 'sort' controla el orden ("visited" | "rating" | "recent"), o 'favorites' para favoritos
  sort: { type: String, required: true },
  seeAllQuery: { type: Object, default: () => ({}) },
  authRequired: { type: Boolean, default: false },
})

const router = useRouter()
const items = ref([])
const loading = ref(false)
const error = ref('')
const rootEl = ref(null)
let observer

function goSeeAll() {
  router.push({ name: 'sites-list', query: props.seeAllQuery })
}
function openDetail(site) {
  router.push({ name: 'site-detail', params: { id: site.id } })
}

async function fetchData() {
  try {
    loading.value = true
    error.value = ''
    if (props.sort === 'favorites') {
      items.value = (await SitesAPI.favorites({ limit: 12 })).items || []
    } else {
      items.value = (await SitesAPI.list({ sort: props.sort, limit: 12 })).items || []
    }
  } catch (e) {
    error.value = e.message || 'Error al cargar'
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
        observer.disconnect()
      }
    },
    { rootMargin: '200px' },
  )
  if (rootEl.value) observer.observe(rootEl.value)
}

onMounted(makeLazy)
onBeforeUnmount(() => observer && observer.disconnect())
</script>

<style scoped>
.section {
  margin: 24px 0;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.section-header h2 {
  font-size: 1.1rem;
  margin: 0;
}
.see-all {
  background: #2fa573;
  color: white;
  border: none;
  border-radius: 999px;
  padding: 6px 12px;
  cursor: pointer;
}
.grid {
  display: grid;
  gap: 12px;
}
/* Breakpoints del enunciado: <767, 768–1024, >1025 */
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
  color: #666;
  font-size: 0.95rem;
}
</style>
