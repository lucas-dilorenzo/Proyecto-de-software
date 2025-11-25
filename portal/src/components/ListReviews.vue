<template>
  <div class="container my-5">    
    <div v-if="props.review.length === 0" class="alert alert-info">No hay review disponibles.</div>
    <div v-else>
      <ReviewComponent
        v-for="review_ in props.review"
        :key="review_.id"
        :review="review_"
        :is-editable="isReviewEditable(review_)"
        @update="handleUpdateReview"
        @delete="handleDeleteReview"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Review } from '@/services/api'
import { onMounted } from 'vue'
import ReviewComponent from './ReviewComponent.vue'

const props = defineProps<{
  review: Review[]
  currentUserReviewId?: number
}>()

const emit = defineEmits<{
  updateReview: [reviewId: number, rating: number, comment: string]
  deleteReview: [reviewId: number]
}>()

function isReviewEditable(review: Review): boolean {
  // Una reseña es editable si:
  // 1. El ID coincide con la reseña del usuario actual
  // 2. La reseña está en estado 'pendiente' (se puede editar solo en este estado)
  
  const isCurrentUser = props.currentUserReviewId !== undefined && review.id === props.currentUserReviewId
  const isPending = review.state?.toLowerCase() === 'pendiente'
  
  return isCurrentUser && isPending
}

function handleUpdateReview(reviewId: number, rating: number, comment: string) {
  emit('updateReview', reviewId, rating, comment)
}

function handleDeleteReview(reviewId: number) {
  emit('deleteReview', reviewId)
}

onMounted(() => {
  console.log('Reseñas recibidas:', props.review)
})
</script>
