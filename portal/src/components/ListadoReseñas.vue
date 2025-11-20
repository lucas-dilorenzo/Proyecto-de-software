<template>
  <!-- <div>class="listado-resenas">
        <h2>Listado de Reseñas</h2>
        <div v-if="review.length === 0" class="alert alert-info">
            No hay review disponibles.
        </div>
        <div v-else>
            <div v-for="reseña in review" :key="reseña.id" class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">{{ reseña.titulo }}</h5>
                    <p class="card-text">{{ reseña.contenido }}</p>
                    <p class="card-text">
                        <small class="text-muted">Calificación: {{ reseña.calificacion }} / 5</small>
                    </p>
                </div>
            </div>
        </div>
    </div> -->
  <div class="container my-5">
    <div v-if="props.review.length === 0" class="alert alert-info">No hay review disponibles.</div>
    <div v-else>
      <div v-for="review_ in props.review" :key="review_.id" class="card mb-3 shadow-sm">
        <div class="card-body">
          <div class="d-flex align-items-start">
            <img
              src="https://api.iconify.design/bi/person-fill.svg" 
              class="rounded-circle me-3"
              alt="Avatar"
              style="width: 50px; height: 50px"
            />            

            <div class="flex-grow-1">
              <!-- <h6 class="mb-1">{{ review_.user_id }}</h6> -->

              <div class="text-warning mb-2 h5">
                <span v-for="star in 5" :key="star">
                  <i
                    class="bi"
                    :class="star <= review_.rating ? 'bi-star-fill' : 'bi-star'"
                  ></i>
                </span>
              </div>

              <p class="mb-2">
                {{ review_.comment }}
              </p>

              <small class="text-muted">
                <i class="bi bi-calendar"></i> Publicado {{ calculateTimePublished(review_.inserted_at) }}
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Review } from '@/services/api'
import { onMounted } from 'vue'
// const review = computed(() => props.review)
const props = defineProps<{
  review: Review[]
}>()

function calculateTimePublished(date: Date): string {
  const publishedDate = new Date(date)
  const currentDate = new Date()
  const diffInMs = currentDate.getTime() - publishedDate.getTime()
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24))

  if (diffInDays === 0) {
    return 'hoy'
  } else if (diffInDays === 1) {
    return 'ayer'
  } else {
    return `hace ${diffInDays} días`
  }
}

onMounted(() => {
  console.log('Reseñas recibidas:', props.review)
})
</script>
