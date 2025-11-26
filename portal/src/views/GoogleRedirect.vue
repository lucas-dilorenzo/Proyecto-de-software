<template>
  <div></div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
const API_URL = import.meta.env.VITE_API_BASE ?? 'https://admin-grupo37.proyecto2025.linti.unlp.edu.ar/api' as string;
onMounted(() => {
  window.location.href = `${API_URL}/auth/google/login`;
})
</script>
