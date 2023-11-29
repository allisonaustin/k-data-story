<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import SpatialView from './components/SpatialView.vue'
</script>

<template>
  <div>
    <header>Rack Layout</header>
    <SpatialView />
  </div>
  <RouterView />
</template>

<style scoped>
header {
  margin-top: 20px
}
</style>
