<script setup lang="ts">
import { defineProps } from 'vue'

defineProps<{ title?: string }>()
</script>

<template>
  <header class="app-toolbar">
    <div class="left">
      <slot name="left">
        <h2>{{ title ?? 'Portal' }}</h2>
      </slot>
    </div>
    <div class="right">
      <slot name="right">
        <!-- placeholder for buttons/controls -->
      </slot>
    </div>
  </header>
</template>

<!-- <style scoped>
.app-toolbar {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid var(--color-border, #e6e6e6);
  position: sticky;
  top: 0;
  z-index: 40;
}
.app-toolbar .left h2 { margin: 0; font-size: 1.1rem }
</style> -->
