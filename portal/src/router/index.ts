import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import authGuard from '@/guards/authGuard'
import maintenanceGuard from '@/guards/maintenanceGuard'

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
    {
      path: '/maintenance',
      name: 'maintenance',
      component: () => import('@/views/MaintenanceView.vue')
    }
  ],
})

router.beforeEach(async (to, from, next) => {
  // Permitir acceso libre a la vista de mantenimiento
  if (to.name === 'maintenance') {
    return next();
  }
  // Ejecutar el maintenanceGuard para el resto
  await maintenanceGuard(to, from, next);
});
router.beforeEach(authGuard);