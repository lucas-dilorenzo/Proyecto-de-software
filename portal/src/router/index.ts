import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'

const SitesList = () => import('@/views/SitesList.vue') // TODO: crear
const SiteDetail = () => import('@/views/SiteDetail.vue') // TODO: crear
const UserDash = () => import('@/views/UserDashboard.vue') // TODO: crear

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/sitios', name: 'sites-list', component: SitesList },
    { path: '/sitios/:id', name: 'site-detail', component: SiteDetail },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/me/favorites', name: 'my-favorites', component: SitesList,},
    { path: '/me/dashboard', name: 'user-dashboard', component: UserDash},
  ],
})
