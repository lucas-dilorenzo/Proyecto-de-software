<template>
  <article class="skeleton-card">
    <div class="ph thumb"></div>
    <div class="ph line w70"></div>
    <div class="ph line w40"></div>
  </article>
</template>

<script setup></script>

<style scoped>
.skeleton-card {
  border: 1px solid #eee;
  border-radius: 12px;
  overflow: hidden;
  padding: 10px;
  background: #fff;
}
.ph {
  background: linear-gradient(90deg, #eee 25%, #f5f5f5 37%, #eee 63%);
  animation: pulse 1.4s ease infinite;
}
.thumb {
  aspect-ratio: 16/9;
  border-radius: 8px;
}
.line {
  height: 12px;
  border-radius: 6px;
  margin-top: 10px;
}
.w70 {
  width: 70%;
}
.w40 {
  width: 40%;
}
@keyframes pulse {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 200% 0;
  }
}
</style>
