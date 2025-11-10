<template>
    <div class="listado-sitios">
        <ListaSitio :sitios="sitios"></ListaSitio>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ListaSitio from '@/components/ListaSitio.vue'

const sitios = ref([
    { id: 1, nombre: 'Sitio 1', descripcion: 'Descripción del Sitio 1' },
    { id: 2, nombre: 'Sitio 2', descripcion: 'Descripción del Sitio 2' },
    { id: 3, nombre: 'Sitio 3', descripcion: 'Descripción del Sitio 3' }
])
</script>

<!-- <style scoped>
.listado-sitios {
    padding: 20px;
    background-color: #1d3221;
    border: 1px solid #68816c;
}
</style>     -->