<template>
  <section class="hero card">
    <div class="wrap">
      <h1 class="title h1">Sitios Históricos</h1>
      <p class="subtitle subtle">Descubrí lugares destacados y experiencias cerca tuyo.</p>
      <form @submit.prevent="goSearch" class="search">
        <input v-model.trim="q" type="search" placeholder="Buscar sitios…" />
        <button class="btn">Buscar</button>
      </form>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const q = ref('')
const router = useRouter()
function goSearch() {
  router.push({ name: 'sites-list', query: { q: q.value } })
}
</script>

<style scoped>
.hero {
  background: var(--card);
  border: 1px solid #eae6df;
  padding: 32px 18px;
}
.wrap {
  max-width: 880px;
  margin: 0 auto;
  text-align: center;
}
.title {
  margin: 0 0 6px;
}
.subtitle {
  margin: 0 0 18px;
}
.search {
  display: flex;
  gap: 10px;
  justify-content: center;
}
.search input {
  flex: 1;
  max-width: 640px;
  padding: 12px 14px;
  border: none;
  border-bottom: 2px solid #d9d4cc;
  background: #f9f7f4;
  border-radius: 10px;
}
.search input:focus {
  outline: none;
  border-bottom-color: #b1a99d;
  background: #fff;
}
.btn {
  padding: 12px 16px;
}
</style>
