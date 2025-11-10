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
  <li class="sitio-item" @click="onSelect">
    <div class="info">
      <strong>{{ sitio.nombre }}</strong>
      <div class="descripcion">{{ sitio.descripcion }}</div>
    </div>
    <div class="actions">
      <button type="button" @click="onEdit" aria-label="Editar">Editar</button>
      <button type="button" @click="onDelete" aria-label="Eliminar">Eliminar</button>
    </div>
  </li>
</template>

<style scoped>
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
</style>
