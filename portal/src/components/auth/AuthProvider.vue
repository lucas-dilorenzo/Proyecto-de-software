<template>
  <slot></slot>
</template>

<script setup lang="ts">
import { authTokenKey } from '@/utils/providerKeys'
import { provide, ref } from 'vue'

const authToken = ref<string>()

function setAuthToken(token: string) {
  authToken.value = token
}

provide(authTokenKey, [authToken, setAuthToken])
</script>
