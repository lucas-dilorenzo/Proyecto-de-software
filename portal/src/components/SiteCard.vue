<template>
  <article class="site-card" @click="$emit('open', site)">
    <div class="thumb">
      <img :src="site.cover_url" :alt="site.name + ' - portada'" loading="lazy" />
    </div>
    <div class="body">
      <h3 class="name">{{ site.name }}</h3>
      <p class="meta">{{ site.city }}, {{ site.province }}</p>
      <p v-if="site.rating != null" class="rating">★ {{ site.rating.toFixed(1) }}</p>
    </div>
  </article>
</template>

<script setup>
const props = defineProps({ site: { type: Object, required: true } })
</script>

<style scoped>
.site-card {
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}
.site-card .thumb {
  aspect-ratio: 16/9;
  background: #f2f2f2;
}
.site-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.site-card .body {
  padding: 10px 12px;
}
.name {
  font-size: 1rem;
  line-height: 1.2;
  margin: 0 0 4px;
}
.meta {
  font-size: 0.85rem;
  color: #666;
  margin: 0;
}
.rating {
  font-size: 0.85rem;
  margin-top: 6px;
  color: #222;
}
</style>
