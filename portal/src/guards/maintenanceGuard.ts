import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router';
import api, { type Flag } from '@/services/api';

async function isUnderMaintenance(): Promise<boolean> {
    // Aquí iría la lógica para verificar si el sistema está en mantenimiento
    // api = /api/flags/status
    const response: { data: Flag } = await api.getFlagsApi().getStatus();
    if (response.data.maintenance_mode) {
        return true;
    }
    return false; 
}

export default async function maintenanceGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) {
  // Lógica de validación
  if (await isUnderMaintenance()) {
    // Si está en mantenimiento, mandar a pantalla de mantenimiento
    next({ name: 'maintenance' });
  } else {
    // Si no está en mantenimiento, continuar
    next();
  }
}