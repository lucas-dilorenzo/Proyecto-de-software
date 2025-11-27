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
          :icon="UserSelectedIcon"
        >
          <l-popup>
            <strong>📍 Punto seleccionado</strong><br>
            Radio: {{ filters.km || 200 }} km<br>
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
          <l-popup>Radio de búsqueda: {{ filters.km || 200 }} km</l-popup>
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
              <a 
                :href="`/sitios/${site.id}`" 
                class="btn btn-primary btn-sm text-white"
                @click.prevent="navigateToSite(site.id)"
              >
                Ver más
              </a>
            </div>
          </l-popup>
          <l-tooltip>
            <strong>{{ site.name }}</strong><br>
            {{ site.description_short || '' }}
          </l-tooltip>
        </l-marker>
      </l-map>
    </div>
    
    <!-- Info de resultados -->
    <div class="mt-2">
      <div v-if="loadingNearbySites" class="alert alert-info py-2 mb-2">
        <div class="d-flex align-items-center">
          <div class="spinner-border spinner-border-sm me-2" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <span>Buscando sitios cercanos...</span>
        </div>
      </div>
      <div v-else-if="userSelectedCenter" class="alert alert-info py-2 mb-2">
        <i class="bi bi-cursor me-1"></i>
        <strong>Punto seleccionado:</strong> {{ filteredSitesByRadius.length }} sitio{{ filteredSitesByRadius.length !== 1 ? 's' : '' }} 
        encontrado{{ filteredSitesByRadius.length !== 1 ? 's' : '' }} dentro de {{ filters.km || 200 }} km.
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
import { LMap, LTileLayer, LMarker, LPopup, LCircle, LTooltip } from "@vue-leaflet/vue-leaflet";
import L from 'leaflet';
import type { Site } from '@/services/api';
import api from '@/services/api';

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

const UserSelectedIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',  
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
const nearbySites = ref<Site[]>([]); // Sitios cercanos al punto seleccionado
const loadingNearbySites = ref(false); // Estado de carga

const widthProp = computed(() => props.width);
const heightProp = computed(() => props.height);

// Radio en metros
const radiusInMeters = computed(() => {
  const km = props.filters.km || 200;
  return km * 1000;
});

// Sitios a mostrar en el mapa (cercanos si hay punto seleccionado, todos si no)
const filteredSitesByRadius = computed(() => {
  if (!userSelectedCenter.value) {
    return props.closeSites;
  }
  return nearbySites.value;
});

// Cargar sitios cercanos desde la API
async function fetchNearbySites(lat: number, lng: number) {
  loadingNearbySites.value = true;
  
  try {
    const params: Record<string, string | number> = {
      lat,
      long: lng,
      radius: props.filters.km || 200,
      page: 1,
      per_page: 100
    };
    
    console.log('🔍 Buscando sitios cercanos:', params);
    
    const response = await api.getSitesApi().list(params);
    nearbySites.value = response.data;
    
    console.log(`✅ Encontrados ${response.data.length} sitios cercanos`);
  } catch (error) {
    console.error('❌ Error al buscar sitios cercanos:', error);
    nearbySites.value = [];
  } finally {
    loadingNearbySites.value = false;
  }
}

// Manejar click en el mapa
async function onMapClick(event: L.LeafletMouseEvent) {
  const { latlng } = event;
  userSelectedCenter.value = [latlng.lat, latlng.lng];
  console.log('🎯 Punto seleccionado:', latlng.lat, latlng.lng);
  
  // Cargar sitios cercanos desde la API
  await fetchNearbySites(latlng.lat, latlng.lng);
}

// Limpiar selección del usuario
function clearSelection() {
  userSelectedCenter.value = null;
  nearbySites.value = [];
  console.log('🧹 Selección limpiada - Mostrando todos los sitios filtrados');
  
  // Recalcular el centro basado en todos los sitios
  calculateMapCenter();
  
  // Actualizar la vista del mapa
  if (isMapReady.value) {
    nextTick(() => {
      updateMapView();
    });
  }
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

// Haversine formula para distancia en km entre dos puntos geográficos
function haversine(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

// Actualizar la vista del mapa según los sitios filtrados
function updateMapView() {
  if (!isMapReady.value) return

  const mapInstance = map.value?.leafletObject as L.Map
  if (!mapInstance) return

  // Invalidar tamaño para asegurar renderizado correcto
  mapInstance.invalidateSize()

  try {
    // Si el usuario seleccionó un punto, centrar en ese punto y los sitios filtrados por radio
    if (userSelectedCenter.value) {
      if (filteredSitesByRadius.value.length > 0) {
        console.log('🗺️ Ajustando vista a', filteredSitesByRadius.value.length, 'sitios cerca del punto');
        
        // Filtrar sitios con coordenadas válidas
        const sitesCoords = filteredSitesByRadius.value
          .filter(site => {
            const hasValidCoords = 
              site.latitude !== null && 
              site.latitude !== undefined && 
              site.longitude !== null && 
              site.longitude !== undefined &&
              !isNaN(site.latitude) &&
              !isNaN(site.longitude);
            
            if (!hasValidCoords) {
              console.warn('⚠️ Sitio con coordenadas inválidas:', site.name);
            }
            return hasValidCoords;
          })
          .map(site => [site.latitude, site.longitude] as L.LatLngTuple);
        
        if (sitesCoords.length > 0) {
          const bounds = L.latLngBounds(sitesCoords);
          bounds.extend(userSelectedCenter.value);
          // Verificar que los bounds sean válidos
          if (bounds.isValid()) {
            // Calcular la distancia máxima entre los extremos de los bounds
            const sw = bounds.getSouthWest();
            const ne = bounds.getNorthEast();
            const maxDistKm = haversine(sw.lat, sw.lng, ne.lat, ne.lng);
            if (maxDistKm < 2000) {
              nextTick(() => {
                mapInstance.fitBounds(bounds, { 
                  padding: [50, 50],
                  maxZoom: 14 
                });
              });
            } else {
              console.warn('⚠️ Bounds demasiado grandes para sitios cercanos, centrando en el punto seleccionado');
              nextTick(() => {
                mapInstance.setView(userSelectedCenter.value!, 10);
              });
            }
          } else {
            console.warn('⚠️ Bounds inválidos, centrando en el punto seleccionado');
            nextTick(() => {
              mapInstance.setView(userSelectedCenter.value!, 10);
            });
          }
        } else {
          console.warn('⚠️ No hay sitios con coordenadas válidas, centrando en punto');
          nextTick(() => {
            mapInstance.setView(userSelectedCenter.value!, 10);
          });
        }
      } else {
        // Si no hay sitios en el radio, solo centrar en el punto seleccionado
        console.log('🗺️ No hay sitios en el radio, centrando en el punto');
        nextTick(() => {
          mapInstance.setView(userSelectedCenter.value!, Math.min(currentZoom.value, 10));
        });
      }
    }
    // Si NO hay punto seleccionado pero HAY sitios filtrados, mostrar todos los sitios
    else if (props.closeSites && props.closeSites.length > 0) {
      console.log('🗺️ Ajustando mapa para mostrar', props.closeSites.length, 'sitios');
      // Filtrar sitios con coordenadas válidas
      const sitesCoords = props.closeSites
        .filter(site => {
          const hasValidCoords = 
            site.latitude !== null && 
            site.latitude !== undefined && 
            site.longitude !== null && 
            site.longitude !== undefined &&
            !isNaN(site.latitude) &&
            !isNaN(site.longitude);
          if (!hasValidCoords) {
            console.warn('⚠️ Sitio con coordenadas inválidas:', site.name, site.latitude, site.longitude);
          }
          return hasValidCoords;
        })
        .map(site => [site.latitude, site.longitude] as L.LatLngTuple);

      if (sitesCoords.length > 0) {
        const bounds = L.latLngBounds(sitesCoords);
        // Calcular la distancia máxima entre los extremos de los bounds
        const sw = bounds.getSouthWest();
        const ne = bounds.getNorthEast();
        const maxDistKm = haversine(sw.lat, sw.lng, ne.lat, ne.lng);
        if (bounds.isValid() && maxDistKm < 2000) {
          nextTick(() => {
            mapInstance.fitBounds(bounds, { 
              padding: [50, 50],
              maxZoom: 12 
            });
          });
        } else {
          console.warn('⚠️ Bounds demasiado grandes o inválidos, centrando en Buenos Aires');
          nextTick(() => {
            mapInstance.setView([props.defaultLat, props.defaultLng], props.defaultZoom);
          });
        }
      } else {
        console.warn('⚠️ No hay sitios con coordenadas válidas');
      }
    } 
    // Si no hay sitios, centrar en la ubicación por defecto
    else {
      nextTick(() => {
        mapInstance.setView(mapCenter.value, props.defaultZoom);
      });
    }
  } catch (error) {
    console.error('❌ Error al actualizar vista del mapa:', error);
    // En caso de error, intentar centrar en la ubicación por defecto
    nextTick(() => {
      if (userSelectedCenter.value) {
        mapInstance.setView(userSelectedCenter.value, 10);
      } else {
        mapInstance.setView(mapCenter.value, props.defaultZoom);
      }
    });
  }
}

// Calcular el centro del mapa basado en los sitios filtrados
function calculateMapCenter() {
  // Si hay un punto seleccionado por el usuario, no recalcular el centro
  if (userSelectedCenter.value) {
    return;
  }
  
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
  
  clearSelection();
  // Solo recalcular el centro si no hay un punto seleccionado por el usuario
  if (!userSelectedCenter.value) {
    calculateMapCenter();
  }
  
  if (isMapReady.value) {
    nextTick(() => {
      updateMapView();
    });
  }
}, { deep: true, immediate: true });

// Observar cambios en los filtros (especialmente el radio)
watch(() => props.filters.km, async (newKm) => {
  console.log('📏 MapFilterComponent - Radio actualizado:', newKm);
  
  // Si hay un punto seleccionado, recargar los sitios cercanos con el nuevo radio
  if (userSelectedCenter.value) {
    const [lat, lng] = userSelectedCenter.value;
    await fetchNearbySites(lat, lng);
  }
  
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
  } else {
    console.log('🧹 Centro limpiado - volviendo a mostrar todos');
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
