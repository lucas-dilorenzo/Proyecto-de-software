<template>
    <div class="dropdown border-top"> <a href="#"
                class="d-flex align-items-center justify-content-center p-3 link-body-emphasis text-decoration-none dropdown-toggle"
                data-bs-toggle="dropdown" aria-expanded="false"> <img src="https://api.iconify.design/bi/person-fill.svg" alt="Usuario"
                  width="24" height="24" class="rounded-circle"> </a>
              <ul v-if="props.loggedIn" class="dropdown-menu text-small shadow" style="">
                <li><a class="dropdown-item" href="#">Profile</a></li>
                <li>
                  <hr class="dropdown-divider">
                </li>
                <li><a class="dropdown-item" @click="logout">Sign out</a></li>
              </ul>
            </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const props = defineProps({
  loggedIn: { type: Boolean, required: true }
});

const authStore = useAuthStore();
const router = useRouter();

const logout = async () => {
  await authStore.logoutUser();
  router.push('/login');
};
</script>