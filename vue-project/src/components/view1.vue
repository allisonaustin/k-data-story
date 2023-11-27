<script setup lang="ts">
defineProps<{
  msg: string
}>()
import * as d3 from "d3";
import { dataStore } from "@/stores/load_data";
import { rowData } from "@/types"
import {ref} from "vue";
import { createPinia } from 'pinia';
import { createApp } from 'vue'
import App from '../App.vue'
function dataProcess() {
  const pinia = createPinia()
  const app = createApp(App)
  app.use(pinia)
  let data = dataStore().data;
  console.log(data)
  // return data
}
// const data = dataProcess();
// let data: Array<rowData> = [];
let data = await d3.csv('../../data/head.csv');
console.log(data[0])
// let data = await d3.csv('../../data/head.csv');
// console.log(data)
</script>

<template>
  <div class="greetings">
    <h1 class="green">{{ msg }}</h1>
    <h3>
      You’ve successfully created a project with
      <a href="https://vitejs.dev/" target="_blank" rel="noopener">Vite</a> +
      <a href="https://vuejs.org/" target="_blank" rel="noopener">Vue 3</a>. What's next?
    </h3>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
