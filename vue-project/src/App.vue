<script lang="ts">
import SpatialView from './components/SpatialView.vue'
import TimeSeries from './components/TimeSeries.vue'
import HeatmapView from './components/HeatmapView.vue'

export default {
  components: {
    SpatialView,
    TimeSeries,
    HeatmapView
  }, 
  data() {
    return {
      tempDataset: 'temp',
      volDataset: 'vol'
    }
  },
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
  <!-- Introduction -->
  <div class="full-width intro">
    <div class="container">
      <p>Large-scale scientific computing facilities operate HPC systems to provide computational and storage resources to users, often to run numerical simulations. These systems can contain thousands of hardware components, and being able to manage data from these components to monitor and explain hardware failure can be difficult.</p>
      <br>
      <p>We provide an interactive presentation of sensor data from the K computer to help inform users on the impact of hardware failure on an HPC system and to reveal anomalies in the data before the error occurs to support error detection.</p>
      <br>
      <p>The data we are using is from the RIKEN Center for Computational Science. It contains one day of data from May 28, 2019, collected every 5 minutes. This data contains a CPU internal error from the L07 rack on the non-disk system board 6 node at 14:52:00.</p>
    </div>
  </div>
  <!-- Part 1 -->
  <v-container id="main-container" class="d-flex flex-column flex-nowrap" fluid>
    <v-row no-gutters class="left-side">
      <v-col>
        <h2>Rack Layout</h2>
        <div class="caption">
          <p>This is a layout of the HPC system. Each square in the grid represents a compute rack. There are a total of 864 racks in the K computer system and each rack contains two BPs and each BP contains 12 system boards (SBs). </p>
        </div>
        <SpatialView />
      </v-col>
    </v-row>
    <v-row no-gutters class="right-side">
      <v-col>
        <TimeSeries :dataset="tempDataset" />
        <TimeSeries :dataset="volDataset" />
      </v-col>
    </v-row>
  </v-container>
  <!-- Part 2 -->  
  <v-container>
    <v-row>
    <h2>Heatmap Layout</h2>
    <HeatmapView />
    </v-row>
  </v-container>
</template>

<style scoped>
#main-container{
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.left-side {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.right-side {
  flex: 1;
  overflow-y: auto; 
  padding: 20px; 
}
</style>