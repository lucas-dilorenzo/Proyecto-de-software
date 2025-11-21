import { useAuthStore } from '@/stores/auth'; // Tu store de autenticación
import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router';

export default function authGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) {
  // Instanciamos el store AQUÍ DENTRO
  const authStore = useAuthStore();

  // Lógica de validación
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    // Si no está logueado, mandar a Login
    next({ name: 'login' });
  } else {
    // Si está logueado o la ruta es pública, continuar
    next();
  }
}
