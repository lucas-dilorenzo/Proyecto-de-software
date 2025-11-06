<template>
  <main class="home-container">
    <!-- Hero opcional -->
    <HeroSearch />

    <section class="sections">
      <SectionStrip
        title="Más visitados"
        sort="rating-5-1"
        :seeAllQuery="{ order_by: 'rating-5-1' }"
      />
      <SectionStrip
        title="Mejor puntuados"
        sort="rating-5-1"
        :seeAllQuery="{ order_by: 'rating-5-1' }"
      />
      <SectionStrip title="Recientes" sort="latest" :seeAllQuery="{ order_by: 'latest' }" />
    </section>

    <footer class="footer">
      <nav>
        <a href="#">Términos</a>
        <a href="#">Privacidad</a>
        <a href="#">Contacto</a>
      </nav>
    </footer>
  </main>
</template>

<script setup lang="ts">
import HeroSearch from '@/components/HeroSearch.vue'
import SectionStrip from '@/components/SectionStrip.vue'
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding: 0 16px 60px; /* 🔹 Agregado padding lateral de 16px */
}

/* 🔹 OPCIONAL: Aumentar padding en pantallas grandes */
@media (min-width: 768px) {
  .home-container {
    padding: 0 24px 60px;
  }
}

@media (min-width: 1025px) {
  .home-container {
    padding: 0 32px 60px;
  }
}

.sections {
  display: flex;
  flex-direction: column;
  gap: 56px;
}

.footer {
  margin-top: 60px;
  padding: 24px 16px;
  border-top: 1px solid #e0dbd3;
  text-align: center;
  color: var(--muted);
}

.footer nav {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.footer a {
  color: inherit;
  text-decoration: none;
  font-size: 0.9rem;
}

.footer a:hover {
  color: var(--fg);
}
</style>
