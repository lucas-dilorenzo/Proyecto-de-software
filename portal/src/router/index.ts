import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import authGuard from '@/guards/authGuard'

const SitesList = () => import('@/views/SitesList.vue') // TODO: crear
const SiteDetail = () => import('@/views/SiteDetail.vue') // TODO: crear
const UserDash = () => import('@/views/UserDashboard.vue') 

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/sitios', name: 'sites-list', component: SitesList },
    { path: '/sitios/:id', name: 'site-detail', component: SiteDetail },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/me/dashboard', name: 'user-dashboard', component: UserDash,
      meta: { requiresAuth: true }
    },
    { path: '/me/favorites', name: 'my-favorites', component: SitesList,
      meta: { requiresAuth: true }
    },
    // login con google, redirigir a la api
    {
      path: '/auth/google',
      name: 'google-redirect',
      component: () => import('@/views/GoogleRedirect.vue')
    },
    // callback de autenticación de Google
    {
      path: '/auth/callback',
      name: 'auth-callback',
      component: () => import('@/views/AuthCallback.vue')
    },
  ],
})

router.beforeEach(authGuard);