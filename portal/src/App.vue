<template>
  <div>
    <header class="topbar">Portal Público</header>
    <router-view />
  </div>
</template>

<script setup></script>

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
