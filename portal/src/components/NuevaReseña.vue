<template>
    <div class="nueva-resena">
        <h2>Nueva Reseña</h2>
        <form @submit.prevent="sendReview()">
            <div class="mb-3">
                <label for="contenido" class="form-label">Contenido</label>
                <textarea v-model="contenido" class="form-control" id="contenido" rows="5" placeholder="Escriba su reseña aquí"></textarea>
            </div>
            <div class="mb-3">
                <label for="calificacion" class="form-label">Calificación</label>
                <StarRatingComponent v-model="rating" />
            </div>
            <div v-if="rating">
                <p>Calificación seleccionada: {{ rating }}</p>
            </div>
            <button type="submit" class="btn btn-primary">Enviar Reseña</button>
        </form>
        
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import StarRatingComponent from './StarRatingComponent.vue'
import api, { type Review } from '@/services/api'
import { logger } from '@/utils/logger'

const rating = ref(0)
const contenido = ref('')
const site_id = ref(0)

const props = defineProps<{
  siteId: number
}>()

site_id.value = props.siteId

async function sendReview() {
  // Aquí puedes manejar el envío de la reseña
  alert(`Reseña: ${contenido.value}\nCalificación: ${rating.value}`)
  const newReview: Review = {
    id: 0, // El ID será asignado por el backend
    site_id: site_id.value,  // Debes asignar el ID del sitio correspondiente
    rating: rating.value,
    comment: contenido.value,
    inserted_at: new Date(),
    updated_at: new Date()
  }
  const response = await api.getSiteReviewsApi(site_id.value).create(newReview, '')
    .then(() => {
      alert('Reseña enviada con éxito')
      // Limpiar el formulario
      contenido.value = ''
      rating.value = 0
    })
    .catch((error) => {
      console.error('Error al enviar la reseña:', error)
      alert('Hubo un error al enviar la reseña')
    })

    logger.log('Reseña enviada', response)
}
</script>