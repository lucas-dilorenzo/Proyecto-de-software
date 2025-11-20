<template>
  <div class="card mb-3 shadow-sm">
    <div class="card-body">
      <div class="d-flex align-items-start">
        <img
          src="https://api.iconify.design/bi/person-fill.svg" 
          class="rounded-circle me-3"
          alt="Avatar"
          style="width: 50px; height: 50px"
        />            

        <div class="flex-grow-1">
          <!-- Modo edición -->
          <div v-if="isEditing">
            <div class="mb-3">
              <label class="form-label">Calificación</label>
              <div class="text-warning mb-2 h5">
                <span v-for="star in 5" :key="star" @click="editedRating = star" style="cursor: pointer;">
                  <i
                    class="bi"
                    :class="star <= editedRating ? 'bi-star-fill' : 'bi-star'"
                  ></i>
                </span>
              </div>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Comentario</label>
              <textarea 
                v-model="editedComment" 
                class="form-control" 
                rows="3"
              ></textarea>
            </div>

            <div class="d-flex gap-2">
              <button @click="saveChanges" class="btn btn-primary btn-sm">
                <i class="bi bi-check-lg"></i> Guardar
              </button>
              <button @click="cancelEdit" class="btn btn-secondary btn-sm">
                <i class="bi bi-x-lg"></i> Cancelar
              </button>
            </div>
          </div>

          <!-- Modo visualización -->
          <div v-else>
            <div class="text-warning mb-2 h5">
              <span v-for="star in 5" :key="star">
                <i
                  class="bi"
                  :class="star <= props.review.rating ? 'bi-star-fill' : 'bi-star'"
                ></i>
              </span>
            </div>

            <div v-if="props.isEditable" class="mb-2">
              <span :class="['badge', badgeClass]">
                Estado: {{ (props.review.state ?? '').toUpperCase() }}
              </span>
            </div>

            <p class="mb-2">
              {{ props.review.comment }}
            </p>

            <div class="d-flex justify-content-between align-items-center">
              <small class="text-muted">
                <i class="bi bi-calendar"></i> Publicado {{ calculateTimePublished(props.review.inserted_at) }}
              </small>

              <!-- Botones de edición/borrado (solo si es editable) -->
              <div v-if="props.isEditable" class="btn-group btn-group-sm">
                <button v-if="props.allowEdit !== false" @click="startEdit" class="btn btn-outline-primary" title="Editar">
                  <i class="bi bi-pencil"></i>Editar
                </button>
                <button @click="confirmDelete" class="btn btn-outline-danger" title="Eliminar">
                  <i class="bi bi-trash"></i>Eliminar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Review } from '@/services/api'
import { ref, computed } from 'vue'

const props = defineProps<{
  review: Review
  isEditable: boolean
  // allowEdit: controls whether the Edit button is shown (defaults to true)
  allowEdit?: boolean
}>()

const emit = defineEmits<{
  update: [reviewId: number, rating: number, comment: string]
  delete: [reviewId: number]
}>()

const isEditing = ref(false)
const editedRating = ref(props.review.rating)
const editedComment = ref(props.review.comment)

const badgeClass = computed(() => {
  const state = (props.review.state ?? '').toUpperCase()
  switch (state) {
    case 'PENDIENTE':
      return 'bg-warning text-dark'
    case 'APROBADA':
      return 'bg-success text-white'
    case 'RECHAZADA':
      return 'bg-danger text-white'
    default:
      return 'bg-info text-dark'
  }
})

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

function startEdit() {
  isEditing.value = true
  editedRating.value = props.review.rating
  editedComment.value = props.review.comment
}

function cancelEdit() {
  isEditing.value = false
  editedRating.value = props.review.rating
  editedComment.value = props.review.comment
}

function saveChanges() {
  emit('update', props.review.id, editedRating.value, editedComment.value)
  isEditing.value = false
}

function confirmDelete() {
  if (confirm('¿Estás seguro de que deseas eliminar esta reseña?')) {
    emit('delete', props.review.id)
  }
}
</script>

<style scoped>
.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
}
</style>
