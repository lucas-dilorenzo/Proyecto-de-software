<template>
  <div class="map-filter-container">
    <div
      class="map-wrapper"
      :style="{ width: widthProp, height: heightProp }"
    >
      <l-map 
        ref="map" 
        v-model:zoom="currentZoom" 
        :center="mapCenter"
        @ready="onMapReady"
        @click="onMapClick"
        :use-global-leaflet="false"
      >
        <l-tile-layer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          layer-type="base"
          name="OpenStreetMap"
        ></l-tile-layer>
        
        <!-- Marcador central (ubicación seleccionada por el usuario) -->
        <l-marker 
          v-if="userSelectedCenter"
          :lat-lng="userSelectedCenter"
        >
          <l-popup>
            <strong>📍 Punto seleccionado</strong><br>
            Radio: {{ filters.km || 50 }} km<br>
            <button 
              @click="clearSelection" 
              class="btn btn-sm btn-outline-danger mt-2"
            >
              Limpiar selección
            </button>
          </l-popup>
        </l-marker>

        <!-- Círculo de radio de búsqueda -->
        <l-circle
          v-if="userSelectedCenter"
          :lat-lng="userSelectedCenter"
          :radius="radiusInMeters"
          :color="'#ff6b6b'"
          :fill-color="'#ff6b6b'"
          :fill-opacity="0.15"
          :weight="2"
        >
          <l-popup>Radio de búsqueda: {{ filters.km || 50 }} km</l-popup>
        </l-circle>

        <!-- Marcadores de sitios filtrados (dentro del radio si hay punto seleccionado) -->
        <l-marker
          v-for="site in filteredSitesByRadius"
          :key="site.id"
          :lat-lng="[site.latitude, site.longitude]"
        >
          <l-popup>
            <div class="site-popup">
              <h6 class="mb-1">{{ site.name }}</h6>
              <p class="mb-2 small text-muted">{{ site.description_short || 'Sin descripción' }}</p>
              <p v-if="userSelectedCenter" class="mb-2 small">
                <i class="bi bi-geo-alt"></i>
                Distancia: {{ calculateDistance(site.latitude, site.longitude, userSelectedCenter[0], userSelectedCenter[1]).toFixed(2) }} km
              </p>
              <a 
                :href="`/sitios/${site.id}`" 
                class="btn btn-primary btn-sm"
                @click.prevent="navigateToSite(site.id)"
              >
                Ver más
              </a>
            </div>
          </l-popup>
        </l-marker>
      </l-map>
    </div>
    
    <!-- Info de resultados -->
    <div class="mt-2">
      <div v-if="userSelectedCenter" class="alert alert-info py-2 mb-2">
        <i class="bi bi-cursor me-1"></i>
        <strong>Punto seleccionado:</strong> Mostrando {{ filteredSitesByRadius.length }} sitio{{ filteredSitesByRadius.length !== 1 ? 's' : '' }} 
        dentro de {{ filters.km || 50 }} km del punto.
        <button @click="clearSelection" class="btn btn-sm btn-link p-0 ms-2">
          Limpiar selección
        </button>
      </div>
      <div v-else-if="closeSites.length > 0" class="text-muted small">
        <i class="bi bi-info-circle me-1"></i>
        {{ closeSites.length }} sitio{{ closeSites.length !== 1 ? 's' : '' }} disponible{{ closeSites.length !== 1 ? 's' : '' }}.
        <strong>Haz clic en el mapa</strong> para filtrar por ubicación.
      </div>
      <div v-else class="text-muted small">
        <i class="bi bi-info-circle me-1"></i>
        No se encontraron sitios con los filtros aplicados
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick, onMounted, type PropType } from 'vue';
import { useRouter } from 'vue-router';
import { LMap, LTileLayer, LMarker, LPopup, LCircle } from "@vue-leaflet/vue-leaflet";
import L from 'leaflet';
import type { Site } from '@/services/api';

// Configurar iconos de Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34]
});

L.Marker.prototype.options.icon = DefaultIcon;

interface Filters {
  city: string;
  province: string;
  tags: string[];
  onlyFavorites: boolean;
  km: number;
}

const props = defineProps({
  width: { type: String, default: '100%' },
  height: { type: String, default: '400px' },
  filters: {
    type: Object as PropType<Filters>,
    required: true
  },
  closeSites: {
    type: Array as PropType<Site[]>,
    default: () => []
  },
  defaultLat: { type: Number, default: -34.6118 }, // Buenos Aires por defecto
  defaultLng: { type: Number, default: -58.3960 },
  defaultZoom: { type: Number, default: 6 },
  showCenterMarker: { type: Boolean, default: true },
  showSearchRadius: { type: Boolean, default: true }
});

const router = useRouter();
const map = ref<InstanceType<typeof LMap> | null>(null);
const currentZoom = ref(props.defaultZoom);
const mapCenter = ref<[number, number]>([props.defaultLat, props.defaultLng]);
const isMapReady = ref(false);
const userSelectedCenter = ref<[number, number] | null>(null); // Centro seleccionado por el usuario

const widthProp = computed(() => props.width);
const heightProp = computed(() => props.height);

// Radio en metros
const radiusInMeters = computed(() => {
  const km = props.filters.km || 50;
  return km * 1000;
});

// Calcular distancia entre dos puntos usando la fórmula de Haversine
function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // Radio de la Tierra en km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

// Filtrar sitios por radio si hay un punto seleccionado
const filteredSitesByRadius = computed(() => {
  if (!userSelectedCenter.value) {
    return props.closeSites;
  }
  
  const [centerLat, centerLng] = userSelectedCenter.value;
  const radiusKm = props.filters.km || 50;
  
  return props.closeSites.filter(site => {
    const distance = calculateDistance(centerLat, centerLng, site.latitude, site.longitude);
    return distance <= radiusKm;
  });
});

// Manejar click en el mapa
function onMapClick(event: L.LeafletMouseEvent) {
  const { latlng } = event;
  userSelectedCenter.value = [latlng.lat, latlng.lng];
  console.log('🎯 Punto seleccionado:', latlng.lat, latlng.lng);
}

// Limpiar selección del usuario
function clearSelection() {
  userSelectedCenter.value = null;
  console.log('🧹 Selección limpiada');
}

// Función llamada cuando el mapa está listo
function onMapReady() {
  isMapReady.value = true
  const mapInstance = map.value?.leafletObject as L.Map
  if (mapInstance) {
    // Forzar recálculo del tamaño del mapa
    setTimeout(() => {
      mapInstance.invalidateSize()
      updateMapView()
    }, 100)
  }
}

// Actualizar la vista del mapa según los sitios filtrados
function updateMapView() {
  if (!isMapReady.value) return

  const mapInstance = map.value?.leafletObject as L.Map
  if (!mapInstance) return

  // Invalidar tamaño para asegurar renderizado correcto
  mapInstance.invalidateSize()

  // Si el usuario seleccionó un punto, centrar en ese punto y los sitios filtrados
  if (userSelectedCenter.value && filteredSitesByRadius.value.length > 0) {
    const bounds = L.latLngBounds(
      filteredSitesByRadius.value.map(site => [site.latitude, site.longitude] as L.LatLngTuple)
    );
    bounds.extend(userSelectedCenter.value);
    
    nextTick(() => {
      mapInstance.fitBounds(bounds, { 
        padding: [50, 50],
        maxZoom: 14 
      });
    });
  }
  // Si hay sitios filtrados pero no hay punto seleccionado, ajustar el mapa para mostrarlos todos
  else if (props.closeSites && props.closeSites.length > 0) {
    const bounds = L.latLngBounds(
      props.closeSites.map(site => [site.latitude, site.longitude] as L.LatLngTuple)
    );

    nextTick(() => {
      mapInstance.fitBounds(bounds, { 
        padding: [50, 50],
        maxZoom: 12 
      });
    });
  } 
  // Si no hay sitios, centrar en la ubicación por defecto
  else {
    nextTick(() => {
      mapInstance.setView(mapCenter.value, props.defaultZoom);
    });
  }
}

// Calcular el centro del mapa basado en los sitios filtrados
function calculateMapCenter() {
  if (props.closeSites && props.closeSites.length > 0) {
    // Calcular el centroide de todos los sitios
    const latSum = props.closeSites.reduce((sum, site) => sum + site.latitude, 0);
    const lngSum = props.closeSites.reduce((sum, site) => sum + site.longitude, 0);
    const count = props.closeSites.length;
    
    mapCenter.value = [latSum / count, lngSum / count];
  } else {
    // Si no hay sitios, usar la ubicación por defecto
    mapCenter.value = [props.defaultLat, props.defaultLng];
  }
}

// Observar cambios en los sitios filtrados
watch(() => props.closeSites, (newSites) => {
  console.log('📍 MapFilterComponent - Sitios actualizados:', newSites?.length || 0);
  calculateMapCenter();
  if (isMapReady.value) {
    nextTick(() => {
      updateMapView();
    });
  }
}, { deep: true, immediate: true });

// Observar cambios en los filtros (especialmente el radio)
watch(() => props.filters.km, (newKm) => {
  console.log('📏 MapFilterComponent - Radio actualizado:', newKm);
  if (isMapReady.value) {
    nextTick(() => {
      updateMapView();
    });
  }
});

// Observar cambios en el punto seleccionado por el usuario
watch(userSelectedCenter, (newCenter) => {
  if (newCenter) {
    console.log('🎯 Centro seleccionado actualizado:', newCenter);
    console.log('📊 Sitios dentro del radio:', filteredSitesByRadius.value.length);
  }
  if (isMapReady.value) {
    nextTick(() => {
      updateMapView();
    });
  }
});

// Navegar a la página de detalle del sitio
function navigateToSite(siteId: number) {
  router.push({ name: 'site-detail', params: { id: siteId } });
}

// Al montar, asegurar que el mapa se redimensione después de un tiempo
onMounted(() => {
  // Esperar un poco para que el DOM se haya renderizado completamente
  setTimeout(() => {
    const mapInstance = map.value?.leafletObject as L.Map;
    if (mapInstance) {
      mapInstance.invalidateSize();
      console.log('🗺️ MapFilterComponent montado y redimensionado');
    }
  }, 300);
});

// Función pública para redimensionar el mapa desde el componente padre
function invalidateMapSize() {
  const mapInstance = map.value?.leafletObject as L.Map;
  if (mapInstance) {
    mapInstance.invalidateSize();
    console.log('🗺️ Mapa redimensionado externamente');
  }
}

// Exponer métodos al componente padre
defineExpose({
  invalidateMapSize
});
</script>

<style scoped>
.map-filter-container {
  width: 100%;
}

.map-wrapper {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

/* Asegurar que el mapa tenga altura */
:deep(.leaflet-container) {
  height: 100%;
  width: 100%;
  min-height: 400px;
  font-family: inherit;
  z-index: 1;
  cursor: crosshair; /* Indicar que se puede hacer clic para seleccionar */
}

.site-popup {
  min-width: 200px;
}

.site-popup h6 {
  font-weight: 600;
  color: #2c3e50;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 8px;
}

:deep(.leaflet-popup-content) {
  margin: 12px;
}

/* Asegurar que los tiles se carguen correctamente */
:deep(.leaflet-tile-container) {
  pointer-events: auto;
}

/* Estilos para el alert de punto seleccionado */
.alert-info {
  border-left: 4px solid #0dcaf0;
  background-color: #cff4fc;
  border-color: #b6effb;
  font-size: 0.9rem;
}

.alert-info .btn-link {
  color: #055160;
  text-decoration: underline;
  font-weight: 500;
}

.alert-info .btn-link:hover {
  color: #022830;
}
</style>
