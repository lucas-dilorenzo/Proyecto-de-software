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
import { computed } from 'vue';
const props = defineProps({
  width: { type: String, default: '100%' },
  height: { type: String, default: '400px' },
  lat: { type: Number, default: -34.6118 },
  lng: { type: Number, default: -58.3960 },
  zoom: { type: Number, default: 6 },
});

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


</script>