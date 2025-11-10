<script setup lang="ts">
import { ref } from 'vue'

const collapsed = ref(false)

function toggle() {
  collapsed.value = !collapsed.value
}
</script>

<template>  
  <aside :class="['app-sidebar d-flex flex-column flex-shrink-0', { collapsed }]">
    <div class="d-flex align-items-center justify-content-between p-3 border-bottom">
      <a href="/" class="d-flex align-items-center text-white text-decoration-none" v-if="!collapsed">
        <span class="fs-5 fw-semibold">Portal</span>
      </a>
      <button 
        class="btn btn-sm btn-outline-light border-0" 
        @click="toggle" 
        :aria-pressed="collapsed"
        :title="collapsed ? 'Expandir' : 'Colapsar'"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-list" viewBox="0 0 16 16">
          <path fill-rule="evenodd" d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"/>
        </svg>
      </button>
    </div>
    
    <div class="flex-grow-1 overflow-auto" v-if="!collapsed">
      <slot>
        <ul class="nav nav-pills flex-column mb-auto">
          <li class="nav-item">
            <router-link :to="{ name: 'home' }" class="nav-link text-white" active-class="active" aria-current="page">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-house-door me-2" viewBox="0 0 16 16">
                <path d="M8.354 1.146a.5.5 0 0 0-.708 0l-6 6A.5.5 0 0 0 1.5 7.5v7a.5.5 0 0 0 .5.5h4.5a.5.5 0 0 0 .5-.5v-4h2v4a.5.5 0 0 0 .5.5H14a.5.5 0 0 0 .5-.5v-7a.5.5 0 0 0-.146-.354L13 5.793V2.5a.5.5 0 0 0-.5-.5h-1a.5.5 0 0 0-.5.5v1.293L8.354 1.146zM2.5 14V7.707l5.5-5.5 5.5 5.5V14H10v-4a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5v4H2.5z"/>
              </svg>
              Home
            </router-link>
          </li>
          <li class="nav-item">
            <router-link :to="{ name: 'listado-sitios' }" class="nav-link text-white" active-class="active">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-list-ul me-2" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M5 11.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm-3 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0 4a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0 4a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/>
              </svg>
              Listado
            </router-link>
          </li>
        </ul>
      </slot>
    </div>

    <div class="border-top p-3" v-if="!collapsed">
      <div class="dropdown">
        <a href="#" class="d-flex align-items-center text-white text-decoration-none dropdown-toggle" id="dropdownUser" data-bs-toggle="dropdown" aria-expanded="false">
          <img src="https://github.com/mdo.png" alt="" width="32" height="32" class="rounded-circle me-2">
          <strong>Usuario</strong>
        </a>
        <ul class="dropdown-menu dropdown-menu-dark text-small shadow" aria-labelledby="dropdownUser">
          <li><a class="dropdown-item" href="#">Configuración</a></li>
          <li><a class="dropdown-item" href="#">Perfil</a></li>
          <li><hr class="dropdown-divider"></li>
          <li><a class="dropdown-item" href="#">Cerrar sesión</a></li>
        </ul>
      </div>
    </div>
  </aside>
</template>

<!-- <style scoped>
.app-sidebar {
  width: 280px;
  background-color: #212529;
  min-height: 100vh;
  flex-shrink: 0;
  transition: width 0.3s ease;
}

.app-sidebar.collapsed {
  width: 60px;
}

.app-sidebar.collapsed .nav-link {
  justify-content: center;
  padding: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  transition: background-color 0.15s ease-in-out;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.active {
  background-color: #0d6efd;
}

.nav-pills .nav-link {
  border-radius: 0.375rem;
  margin: 0.25rem 0.5rem;
}

/* Ajustes para el botón de toggle */
.btn-outline-light.border-0:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* Scrollbar personalizado para el sidebar */
.overflow-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.overflow-auto::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.overflow-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style> -->
