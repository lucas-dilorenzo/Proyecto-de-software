<template>
  <div
    class="map-container"
    :style="{ width: widthProp, height: heightProp }"
  >
    <l-map ref="map" v-model:zoom="zoom" :center="[lat, lng]">
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer-type="base"
        name="OpenStreetMap"
      ></l-tile-layer>
      <l-marker :lat-lng="coordinates" draggable> </l-marker>
    </l-map>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, type PropType } from 'vue';
import { type Site } from '@/services/api';

const props = defineProps({
  width: { type: String, default: '100%' },
  height: { type: String, default: '400px' },
  lat: { type: Number, default: -34.6118 },
  lng: { type: Number, default: -58.3960 },
  zoom: { type: Number, default: 6 },
  closeSites: { type: Array as PropType<Site[]>, default: () => [] },
  radius: { type: Number, default: 50 },
});

const map = ref<InstanceType<typeof LMap> | null>(null);

const widthProp = computed(() => props.width);
const heightProp = computed(() => props.height);
const coordinates = computed(() => <L.LatLngExpression>([props.lat, props.lng]));
const lat = computed(() => props.lat);
const lng = computed(() => props.lng);
const zoom = computed(() => props.zoom);

import { LMap, LTileLayer, LMarker } from "@vue-leaflet/vue-leaflet";
import L from 'leaflet';

import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

onMounted(() => {
  if (props.closeSites && props.closeSites.length > 0) {
    console.log('✅ Close sites provided:', props.closeSites);
    
    // Esperar a que el mapa esté listo
    setTimeout(() => {
      const mapInstance = map.value?.leafletObject as L.Map;
      
      if (mapInstance) {
        // Agregar marcadores al mapa
        props.closeSites.forEach((site: Site) => {
          const marker = L.marker([site.latitude, site.longitude]).addTo(mapInstance);
          marker.bindPopup(`<b>${site.name}</b><br>${site.description || ''}`);
        });
        
        // Agregar círculo de radio
        const circle = L.circle([props.lat, props.lng], {
          color: 'blue',
          fillColor: '#blue',
          fillOpacity: 0.1,
          radius: props.radius * 1000, // convertir km a metros
        }).addTo(mapInstance);
        circle.bindPopup(`Radio de ${props.radius} km`);
      }
    }, 100);
  } else {
    console.log('ℹ️ No close sites provided');
  }
});

</script>