<template>
    <div v-if="si_favs">
        MOSTRANDO SITIOS FAVORITOS
    </div>
    <div v-else>
        MOSTRANDO RESEÑAS
    </div>

</template>

<script setup lang="ts">
import { computed } from 'vue';


const props = defineProps<{
    si_favs: boolean;
}>();


</script>