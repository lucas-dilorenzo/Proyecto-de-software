<script setup lang="ts">
import { RouterView } from 'vue-router'
import Sidebar from './components/shared/AppSidebar.vue'
import Toolbar from './components/shared/AppToolbar.vue'
</script>

<template>
  <div class="d-flex min-vh-100 bg-dark text-white">
    <!-- Sidebar a la izquierda -->
    <Sidebar />
    
    <!-- Contenido principal a la derecha -->
    <div class="d-flex flex-column flex-fill">
      <!-- Toolbar arriba -->
      <Toolbar class="navbar navbar-dark bg-dark shadow-sm flex-shrink-0">
        <template #left>
          <div class="navbar-brand ms-2">Portal</div>
        </template>
        <template #right>
          <!-- toolbar actions could go here -->
        </template>
      </Toolbar>
      
      <!-- Contenido de las vistas -->
      <main class="flex-fill p-4 overflow-auto">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.navbar-brand { 
  font-weight: 600;
}

@media (max-width: 768px) {
  .d-flex.min-vh-100 { 
    flex-direction: column !important;
  }
}
</style>
