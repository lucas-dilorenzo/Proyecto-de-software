<template>
    <div v-if="isLoggedIn" class="card p-4 shadow-sm mx-auto mt-5" style="max-width: 400px;">
        <div class="mb-3 text-center">
            <h4 class="mb-2">Sesión iniciada</h4>
        </div>
        <ul class="list-group list-group-flush mb-3">
            <li class="list-group-item"><strong>Usuario:</strong> {{authUser.usuario}}</li>
            <li class="list-group-item"><strong>Mail:</strong> {{authUser.email}}</li>
        </ul>
        <div class="d-grid">
            <button type="button" class="btn btn-outline-danger" @click="logout">Cerrar sesión</button>
        </div>
    </div>
    <div v-else>
        <form class="card p-4 shadow-sm mx-auto" style="max-width: 400px;" @submit.prevent="login">
            <h4 class="mb-3 text-center">Iniciar sesión</h4>
            <div class="mb-3">
                <label class="form-label" for="email">Email:</label>
                <input v-model="user.email" placeholder="Email" class="form-control" type="email" id="email" required>
            </div>
            <div class="mb-3">
                <label class="form-label" for="password">Contraseña:</label>
                <input v-model="user.password" placeholder="Password" type="password" autocomplete="on" class="form-control" id="password" required>
            </div>
            <div v-if="error" class="alert alert-danger py-2">Has introducido mal el email o la contraseña.</div>
            <div class="d-grid">
                <button class="btn btn-primary" type="submit">Login</button>
            </div>
        </form>
        <div class="mt-3 text-center">
            <router-link :to="{ name: 'google-redirect' }" class="btn btn-danger">
                <i class="bi bi-google"></i> Iniciar sesión con Google
            </router-link>
        </div>            
    </div>    
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const error = ref(false);
const user = ref({
    email: "",
    password: "",
    token: ""
});

const router = useRouter();
const authStore = useAuthStore();
const authUser = computed(() => authStore.user);
const isLoggedIn = computed(() => authStore.isLoggedIn);

const login = async () => {
    if (!user.value.email || !user.value.password) {
        error.value = true;
        return;
    }
    try {
        await authStore.loginUser(user.value);
        if (isLoggedIn.value) {
            router.push('/login');
        }
        //redirect to home
        router.push('/');
    } catch (e) {
        console.log(e);
        error.value = true;
    }
};

const logout = async () => {
    try {
        await authStore.logoutUser();
    } catch (e) {
        console.log(e);
    }
    error.value = false;
    user.value = {
        email: "",
        password: "",
        token: ""
    };
    router.push('/');
};
</script>
