<script lang="ts">
import SpatialView from './components/SpatialView.vue'
import TimeSeries from './components/TimeSeries.vue'
import HeatmapView from './components/HeatmapView.vue'
import RadarChart from './components/RadarChart.vue'
// import HeatmapView_vol from './components/HeatmapView_vol.vue'

export default {
  components: {
    SpatialView,
    TimeSeries,
    HeatmapView,
    RadarChart
  }, 
  data() {
    return {
      tempDataset: 'temp',
      volDataset: 'vol',
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
  <div class="full-width container">
    <div id="main-container" class="fixed-container">
      <div class="fixed-left">
        <div id="rack-space">
          <h2>Rack Layout</h2>
          <div class="caption">
            <p>This is a layout of the HPC system. Each square in the grid represents a compute rack. There are a total of 864 racks in the K computer system and each rack contains two BPs and each BP contains 12 system boards (SBs). </p>
          </div>
          <SpatialView/>
        </div>
      </div>
      <div class="scrollable-right">
        <div class="inner">
          <TimeSeries id="timeSeriesTemp" :dataset="tempDataset" />
          <TimeSeries id="timeSeriesVol" :dataset="volDataset" />
        </div>
      </div>
    </div>
  </div>
  <!-- Part 2 -->
  <div class="full-width container">
    <h2>Temperature Heatmap</h2>
    <div class="intro">
      <p>The following heatmaps compare the temperature values between each node in error rack L07. For each node, the left map shows the data before the error occured, and the right map shows the data after the error occured. 
        The colored one represents the error node. </p>
    </div>
    <div id="sec-container" class="full-width container">
          <HeatmapView :dataset="tempDataset" />
    </div>
  </div>
  <!-- Part 3 -->
    <div class="full-width">
      <h2 style="padding-top:20px">System View</h2>
      <div>
        <p>The following radar charts are the snapshots of three different time slot. Each of them shows the deviation between the error node l07 and the neighboring node around it. An axis scales on the min and max of that variable. Hover on the legend will show the specific rack on the snapshots.</p>
      </div>
      <div class="radar-container">
        <div class="row-container">
          <div class="col">
            <RadarChart id="radar-1" dataset="0"/>
          </div>
          <div class="col">
            <RadarChart id="radar-2" dataset="1"/>
          </div>
          <div class="col">
            <RadarChart id="radar-3" dataset="2"/>
          </div>
        </div>
      </div>   
    </div>   
      
</template>

<style scoped>
.fixed-container {
  display: flex;
  padding-bottom: 40px;
}

.radar-container {
  display: flex;
}

#rack-space {
  position: sticky;
  top: 0;
  padding-top: 20px;
}
.fixed-left {
  flex: 0 0 auto;
  padding: 20px; 
  width: auto;
  max-width: 500px;
  text-align: left;
  position: sticky;
  top: 0;
}

.fixed-left-heat {
  flex: 0 0 auto;
  padding: 20px; 
  width: auto;
  max-width: 700px;
  text-align: left;
  position: sticky;
  top: 0;
}

.scrollable-right {
  flex: 1;
  padding-left: 40px;
  padding-top: 40px;
}

#sec-container {
  background-color: #e9e4e499;
}
.col {
  flex: 1;
  flex-direction: column;
  margin: 0;
}
@media (max-width: 1200px) {
    .col {
        width: 100%;
        margin-right: 10px; 
        flex: 1;
    }
}
.row-container {
  display: flex;
  width: 100%; 
}
</style>