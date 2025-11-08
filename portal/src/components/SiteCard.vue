<template>
  <article class="card h-100 border-0 shadow-sm site-card" @click="$emit('open', site)">
    <div class="card-img-top overflow-hidden" style="aspect-ratio: 16/9;">
      <img 
        :src="imgSrc" 
        :alt="site.name + ' - portada'" 
        class="w-100 h-100 object-fit-cover"
        loading="lazy" 
        @error="onImgError" 
      />
    </div>
    <div class="card-body p-3">
      <h3 class="card-title h6 fw-semibold mb-2">{{ site.name }}</h3>
      <p class="text-muted small mb-1">{{ site.city }}, {{ site.province }}</p>
      <p v-if="rating !== null" class="mb-0 small">
        <span class="text-warning">★</span> {{ rating.toFixed(1) }}
      </p>
    </div>
  </article>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { logger } from '@/utils/logger'

const props = defineProps<{ site: any }>()

defineEmits<{
  open: [site: any]
}>()

const PLACEHOLDER = '/placeholder.svg'

const imgSrc = ref(props.site.cover_image || props.site.cover_url || PLACEHOLDER)

watch(
  () => props.site,
  (newSite) => {
    imgSrc.value = newSite.cover_image || newSite.cover_url || PLACEHOLDER
    logger.log('🔄 SiteCard updated:', newSite.name)
  },
  { deep: true },
)

function onImgError() {
  imgSrc.value = PLACEHOLDER
  logger.log('⚠️ SiteCard image error, using placeholder')
}

const rating = computed(() => {
  const r = props.site.avg_rating ?? props.site.rating
  return typeof r === 'number' ? r : null
})
</script>

<style scoped>
.site-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.site-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.object-fit-cover {
  object-fit: cover;
}
</style>
