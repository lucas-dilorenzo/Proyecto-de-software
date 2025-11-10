import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/sitios/listado',
      name: 'listado-sitios',
      component: () => import('../views/ListadoSitios.vue'),
    }
  ],
})

export default router
