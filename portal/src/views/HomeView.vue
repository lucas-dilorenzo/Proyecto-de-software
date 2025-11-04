<template>
  <main class="container">
    <HeroSearch />

    <SectionStrip title="Más visitados" sort="visited" :seeAllQuery="{ sort: 'visited' }" />
    <SectionStrip title="Mejor puntuados" sort="rating" :seeAllQuery="{ sort: 'rating' }" />

    <!-- Solo se muestra Favoritos si hay sesión (flexible: controla desde App.vue o prop) -->
    <SectionStrip
      v-if="isLogged"
      title="Favoritos"
      sort="favorites"
      :seeAllQuery="{ favorites: 1 }"
      :authRequired="true"
    />

    <SectionStrip title="Recientemente agregados" sort="recent" :seeAllQuery="{ sort: 'recent' }" />
  </main>
</template>

<script setup>
import SectionStrip from '@/components/SectionStrip.vue'
import HeroSearch from '@/components/HeroSearch.vue'
// Estrategia mínima: detectar cookie de sesión; si usan token, reemplazar por un store real
const isLogged = document.cookie.includes('session=')
</script>

<style scoped>
.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 16px;
}
</style>
