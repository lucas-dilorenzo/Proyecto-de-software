<script setup lang="ts">
import SitioItem from './SitioItem.vue'

defineProps<{
  sitios: Array<{ id: number; nombre: string; descripcion: string }>;
}>();

const emit = defineEmits<{
  (e: 'select', id: number): void
  (e: 'edit', id: number): void
  (e: 'delete', id: number): void
}>()

function onSelect(id: number) { emit('select', id) }
function onEdit(id: number) { emit('edit', id) }
function onDelete(id: number) { emit('delete', id) }
</script>
<template>
  <div class="listado-sitios">
    <h1>Listado de Sitios</h1>
    <ul>
      <SitioItem
        v-for="sitio in sitios"
        :key="sitio.id"
        :sitio="sitio"
        @select="onSelect"
        @edit="onEdit"
        @delete="onDelete"
      />
    </ul>
  </div>
</template>
<style scoped>
.listado-sitios {
  padding: 20px;
  background-color: #1b221a;
  border: 1px solid #676767;
}
</style>