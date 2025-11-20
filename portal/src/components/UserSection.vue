<template>
    <div v-if="si_favs">
        <header class="d-flex justify-content-between align-items-baseline mb-3">
            <h2 class="h4 mb-0" style="font-family: 'Playfair Display', serif" >Tus sitios favoritos</h2> <!-- tiene que estar centrado -->
        </header>
        <div v-if="error" class="alert alert-danger" role="alert">Error: {{ error }}</div>

        <div v-else>
        <div v-if="loading" class="row row-cols-2 row-cols-md-3 row-cols-lg-4 g-3">
            <div class="col" v-for="i in 6" :key="i">
            <SkeletonCard />
            </div>
        </div>

        <div v-else-if="items.length === 0" class="text-center py-3">
            <span class="badge rounded-pill bg-light text-muted border px-3 py-2">
                Todavía no elegiste sitios favoritos
            </span>
        </div>

        <div v-else class="row row-cols-2 row-cols-md-3 row-cols-lg-4 g-3">
            <div class="col" v-for="s in items" :key="s.id">
                <SiteCard :site="s" @open="openDetail" />
            </div>
        </div>
        </div>

    </div>
    <div v-else>
        <header class="d-flex justify-content-between align-items-baseline mb-3">
            <h2 class="h4 mb-0" style="font-family: 'Playfair Display', serif">Tus reseñas hechas</h2>
        </header>

        <div v-if="error" class="alert alert-danger" role="alert">Error: {{ error }}</div>
        <div v-else-if="reviews.length === 0" class="text-center py-3">
            <span class="badge rounded-pill bg-light text-muted border px-3 py-2">
                Todavía no hiciste una reseña, ¡apurate a hacer una!
            </span>
        </div>
        <div v-else >
            <div v-for="reviews in reviews" :key="reviews.id" class="mb-4">
                <ReviewComponent :review="reviews" :is-editable="true" @update="handleUpdateReview" 
                    @delete="handleDeleteReview"/>
            </div>
        </div>

    </div>

</template>

<script setup lang="ts">
import SkeletonCard from './SkeletonCard.vue';
import SiteCard from './SiteCard.vue';
import api, { Review } from '@/services/api';
import ListReviews from './ListReviews.vue';
import { computed, onMounted, ref } from 'vue';
import { router } from '@/router';
import { type Site } from '@/services/api';
import { logger } from '@/utils/logger';
import ReviewComponent from './ReviewComponent.vue';

const error = ref('')
const loading = ref(false)
const items = ref<Site[]>([])
const reviews = ref<Review[]>([])
const emit = defineEmits<{
  updateReview: [reviewId: number, rating: number, comment: string]
  deleteReview: [reviewId: number]
}>()
const props = defineProps<{
    si_favs: boolean;
}>();

onMounted(async () => {
  logger.log('✅ HomeView mounted')
  loading.value = true
  try {
    const response = await getFavs()
    const responseReviews = await getReviews() 
    items.value = response.data
    reviews.value = responseReviews.data
    error.value = ''
  } catch (err) {
    logger.log('❌ Error:', err)
    error.value = String(err)
    items.value = []
    reviews.value = []
  } finally {
    loading.value = false
  }
})

function openDetail(site: Site) {
  router.push({ name: 'site-detail', params: { id: site.id } })
}

function handleUpdateReview(reviewId: number, rating: number, comment: string) {
  emit('updateReview', reviewId, rating, comment)
}

function handleDeleteReview(reviewId: number) {
  emit('deleteReview', reviewId)
}

async function getFavs(){
  return await api.getUserApi().getFavorites({},'')
}

async function getReviews(){
  return await api.getUserApi().getReviews('')
}


</script>