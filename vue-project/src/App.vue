<script lang="ts">
import SpatialView from './components/SpatialView.vue'
import TimeSeries from './components/TimeSeries.vue'

export default {
  components: {
    SpatialView,
    TimeSeries
  }
}
</script>

<template>
  <div class="full-width header">
    <div class="full-width header-inner">
        <div class="title col-sm-8">
          <h1>Visualizing HPC Data</h1>
          <h2>A visual story of hardware failure in high-performance computing (HPC) systems</h2>
          <p class="authors">
            Allison Austin and Yu-Chia Huang
          </p>
        </div>
    </div>
  </div>
  <v-container id="main-container" class="d-flex flex-column flex-nowrap" fluid>
    <v-row no-gutters>
      <v-col>
        <h2>Rack Layout</h2>
        <SpatialView />
      </v-col>
      <v-col>
        <TimeSeries />
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
#main-container{
  width: 100%;
}
</style>