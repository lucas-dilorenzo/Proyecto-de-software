<script setup lang="ts">
import { defineEmits, defineProps } from 'vue'

const props = defineProps<{ sitio: { id: number; nombre: string; descripcion: string } }>()
const emit = defineEmits<{
  (e: 'select', id: number): void
  (e: 'edit', id: number): void
  (e: 'delete', id: number): void
}>()

function onSelect() {
  emit('select', props.sitio.id)
}

function onEdit(e: Event) {
  e.stopPropagation()
  emit('edit', props.sitio.id)
}

function onDelete(e: Event) {
  e.stopPropagation()
  emit('delete', props.sitio.id)
}
</script>

<template>
  <li class="sitio-item list-group-item d-flex justify-content-between align-items-start" @click="onSelect">
    <div class="info ms-2 me-auto">
      <div class="fw-bold">
        {{ sitio.nombre }}
      </div>
      <div class="descripcion">{{ sitio.descripcion }}</div>
    </div>
    <div class="actions">
      <div class="btn-group" role="group" aria-label="Basic outlined example">
        <button class="btn btn-sm btn-outline-secondary" type="button" @click="onEdit" aria-label="Editar">Editar</button>
        <button class="btn btn-sm btn-outline-danger" type="button" @click="onDelete" aria-label="Eliminar">Eliminar</button>
      </div>
    </div>
  </li>
</template>

<!-- <style scoped>
.sitio-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #eee;
}
.sitio-item:hover {
  background: #fff;
}
.info { flex: 1 }
.descripcion { color: #666; font-size: 0.9em }
.actions { display: flex; gap: 8px }
.actions button { padding: 4px 8px; font-size: 0.9em }
</style> -->
