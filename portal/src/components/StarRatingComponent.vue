<template>
  <div class="star-rating">
    <span
      v-for="star in maxStars"
      :key="star"
      class="star"
      :class="{ filled: star <= currentValue }"
      @click="selectStar(star)"
      @mouseover="hoverStar(star)"
      @mouseleave="hoverStar(0)"
      >
      ★
    </span>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 0 },
  maxStars: { type: Number, default: 5 }
})
const emit = defineEmits(['update:modelValue'])

const currentValue = ref(props.modelValue)
const hoverValue = ref(0)

watch(() => props.modelValue, (val) => {
  currentValue.value = val
})

function selectStar(star: number) {
  emit('update:modelValue', star)
  currentValue.value = star
}

function hoverStar(star: number) {
  hoverValue.value = star
  currentValue.value = star || props.modelValue
}
</script>

<style scoped>
.star-rating {
  display: flex;
  flex-direction: row;
  gap: 0.2em;
  font-size: 2rem;
  cursor: pointer;
}
.star {
  color: #ccc;
  transition: color 0.2s;
}
.star.filled {
  color: #FFD700;
}
</style>
