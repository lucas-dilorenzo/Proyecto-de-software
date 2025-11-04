<template>
  <main style="padding: 16px">
    <h1>Detalle del Sitio #{{ id }}</h1>
  </main>
</template>
<script setup lang="ts">
import { useRoute } from 'vue-router'
const id = Number(useRoute().params.id)
</script>
