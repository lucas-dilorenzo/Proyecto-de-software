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

        <!-- <div v-else-if="items.length === 0" class="text-center py-3">
            <span class="badge rounded-pill bg-light text-muted border px-3 py-2">
                Todavía no elegiste sitios favoritos.
            </span>
        </div> -->
    </div>
    <div v-else>
        <header class="d-flex justify-content-between align-items-baseline mb-3">
            <h2 class="h4 mb-0" style="font-family: 'Playfair Display', serif">Reseñas hechas</h2>
        </header>
    </div>

</template>

<script setup lang="ts">
import SkeletonCard from './SkeletonCard.vue';
import SiteCard from './SiteCard.vue';
import api from '@/services/api';
import { computed, onMounted, ref } from 'vue';
import { router } from '@/router';
import { type Site } from '@/services/api';
import { logger } from '@/utils/logger';

const error = ref('')
const loading = ref(false)
const items = ref<Site[]>([])
const props = defineProps<{
    si_favs: boolean;
}>();

onMounted(async () => {
  logger.log('✅ HomeView mounted')
  loading.value = true
  try {
    const response = await getFavs()
    items.value = response.data
    error.value = ''
  } catch (err) {
    logger.log('❌ Error fetching favorites:', err)
    error.value = 'No se pudieron cargar los sitios favoritos'
    items.value = []
  } finally {
    loading.value = false
  }
})

function openDetail(site: Site) {
  router.push({ name: 'site-detail', params: { id: site.id } })
}

async function getFavs(){
  return await api.getUserApi().getFavorites({},'')
}


</script>