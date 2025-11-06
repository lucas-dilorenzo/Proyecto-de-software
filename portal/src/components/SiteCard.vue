<template>
  <article class="site-card card" @click="$emit('open', site)">
    <div class="thumb">
      <img
        :src="imgSrc"
        :alt="site.name + ' - portada'"
        loading="lazy"
        referrerpolicy="no-referrer"
        @error="onImgError"
      />
    </div>
    <div class="body">
      <h3 class="name">{{ site.name }}</h3>
      <p class="meta">{{ site.city }}, {{ site.province }}</p>
      <p v-if="rating !== null" class="rating">★ {{ rating.toFixed(1) }}</p>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = defineProps<{ site: any }>()

// normalizamos keys del backend
const cover = computed<string>(() => props.site.cover_url ?? props.site.cover_image ?? '')
const rating = computed<number | null>(() => {
  const r = props.site.rating ?? props.site.avg_rating
  return typeof r === 'number' ? r : null
})

// placeholder local (poner un archivo en portal/public/placeholder.jpg)
const FALLBACK = '/placeholder.jpg'

const imgSrc = ref(cover.value || FALLBACK)
watch(cover, (val) => {
  imgSrc.value = val || FALLBACK
})

function onImgError() {
  if (imgSrc.value !== FALLBACK) {
    imgSrc.value = FALLBACK
  }
}
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
.site-card .thumb {
  aspect-ratio: 16/9;
  background: #f2f0ec;
}
.site-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.site-card .body {
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
