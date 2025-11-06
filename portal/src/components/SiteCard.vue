<template>
  <article class="site-card card" @click="$emit('open', site)">
    <div class="thumb">
      <img :src="imgSrc" :alt="site.name + ' - portada'" loading="lazy" @error="onImgError" />
    </div>
    <div class="body">
      <h3 class="name">{{ site.name }}</h3>
      <p class="meta">{{ site.city }}, {{ site.province }}</p>
      <p v-if="rating !== null" class="rating">★ {{ rating.toFixed(1) }}</p>
    </div>
  </article>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{ site: any }>()

const PLACEHOLDER = '/placeholder.svg'

const imgSrc = ref(props.site.cover_image || props.site.cover_url || PLACEHOLDER)

watch(
  () => props.site,
  (newSite) => {
    imgSrc.value = newSite.cover_image || newSite.cover_url || PLACEHOLDER
  },
  { deep: true },
)

function onImgError() {
  imgSrc.value = PLACEHOLDER
}

const rating = computed(() => {
  const r = props.site.avg_rating ?? props.site.rating
  return typeof r === 'number' ? r : null
})
</script>

<style scoped>
.site-card {
  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease;
}
.site-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.06);
}
.thumb {
  aspect-ratio: 16/9;
  background: #f2f0ec;
  border-radius: 10px 10px 0 0;
  overflow: hidden;
}
.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.body {
  padding: 12px 14px;
}
.name {
  font-size: 1.05rem;
  line-height: 1.2;
  margin: 0 0 6px;
  font-weight: 600;
}
.meta {
  font-size: 0.9rem;
  color: #6b7280;
  margin: 0;
}
.rating {
  font-size: 0.9rem;
  margin-top: 8px;
  color: #111;
}
</style>
