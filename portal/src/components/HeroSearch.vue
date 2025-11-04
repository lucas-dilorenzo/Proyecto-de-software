<template>
  <section class="hero">
    <div class="wrap">
      <h1 class="title">Sitios Históricos</h1>
      <form @submit.prevent="goSearch" class="search">
        <input v-model.trim="q" type="search" placeholder="Buscar sitios…" />
        <button>Buscar</button>
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
  background: linear-gradient(135deg, #2fa573, #1b7250);
  color: #fff;
  padding: 28px 16px;
  border-radius: 16px;
}
.wrap {
  max-width: 1100px;
  margin: 0 auto;
}
.title {
  margin: 0 0 12px;
}
.search {
  display: flex;
  gap: 8px;
}
.search input {
  flex: 1;
  padding: 10px;
  border-radius: 10px;
  border: none;
}
.search button {
  padding: 10px 14px;
  border: none;
  border-radius: 10px;
  background: #fff;
  color: #1b7250;
  font-weight: 600;
  cursor: pointer;
}
</style>
