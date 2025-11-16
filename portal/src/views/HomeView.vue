<template>
  <main class="container-fluid px-3 px-md-4 pb-5">
    <HeroSearch />

    <section class="row g-4 g-md-5 my-4">
      <div class="col-12">
        <SectionStrip
          title="Más visitados"
          sort="rating-5-1"
          :seeAllQuery="{ order_by: 'rating-5-1' }"
        />
      </div>
      <div class="col-12">
        <SectionStrip
          title="Mejor puntuados"
          sort="rating-5-1"
          :seeAllQuery="{ order_by: 'rating-5-1' }"
        />
      </div>
      <div class="col-12">
        <SectionStrip title="Recientes" sort="latest" :seeAllQuery="{ order_by: 'latest' }" />
      </div>
    </section>

    <footer class="border-top text-center mt-5 pt-4 pb-3">
      <nav class="d-flex justify-content-center gap-3 flex-wrap">
        <a href="#" class="text-muted text-decoration-none small">Términos</a>
        <a href="#" class="text-muted text-decoration-none small">Privacidad</a>
        <a href="#" class="text-muted text-decoration-none small">Contacto</a>
      </nav>
    </footer>
  </main>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import HeroSearch from '@/components/HeroSearch.vue'
import SectionStrip from '@/components/SectionStrip.vue'
import { logger } from '@/utils/logger'

onMounted(() => {
  logger.log('✅ HomeView mounted')
})
</script>

<style scoped></style>
