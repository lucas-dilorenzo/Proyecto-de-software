<template>
  <div>
    <header class="topbar">Portal Público</header>
    <div class="container"><router-view /></div>
  </div>
</template>

<script setup>
console.log('✅ App mounted')
</script>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  background: #fff;
  border-bottom: 1px solid #eee;
  padding: 12px 16px;
  font-weight: 600;
  z-index: 10;
}
</style>
