<template>
    
    <section class="card border-0 shadow-sm mb-4">
        <div class="card-body py-4 py-md-5 px-3 px-md-4">
            <div class="text-center mx-auto" style="max-width: 880px">
                <h1 class="display-5 fw-bold mb-2">¡Bienvenido {user}!</h1>
                <p class="text-muted mb-4">Descubrí lugares destacados y experiencias cerca tuyo.</p>
                <div class="d-flex gap-2 justify-content-center">
                    <button class="btn btn-primary btn-lg" @click="goFavs()">Mis sitios favoritos</button>
                    <button class="btn btn-primary btn-lg" @click="goReviews()">Mis reseñas</button>
                </div>
            </div>
        </div>
    </section>    
                
    <main class="container-fluid px-3 px-md-4 pb-5">
        <div>
            <UserSection
                :si_favs="si_favs"
            /> 
        </div>

        <footer class="border-top text-center mt-5 pt-4 pb-3">
          <nav class="d-flex justify-content-center gap-3 flex-wrap">
            <a href="#" class="text-muted text-decoration-none small">Términos</a>
            <a href="#" class="text-muted text-decoration-none small">Privacidad</a>
            <a href="#" class="text-muted text-decoration-none small">Contacto</a>
          </nav>
        </footer>

    </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import UserSection from '@/components/UserSection.vue';
import { logger } from '@/utils/logger';

const si_favs = ref(true);

onMounted(() => {
  logger.log('✅✅✅ UserDashboard mounted') 
})

function goFavs() {
  si_favs.value = true;
}

function goReviews() {
  si_favs.value = false;
}
</script>

<style scoped></style>
