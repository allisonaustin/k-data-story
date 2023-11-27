import { defineStore } from 'pinia';
import * as d3 from "d3";
import type { rowData } from '../types';

export const dataStore = defineStore('data', {
  state: () => {
    const data: Array<rowData> = [];
    // const type_colors = {
    //   Normal: "#aa9",
    //   Fire: "#f42",
    //   Water: "#39f",
    //   Electric: "#fc3",
    //   Grass: "#7c5",
    //   Ice: "#6cf",
    //   Fighting: "#b54",
    //   Poison: "#a59",
    //   Ground: "#db5",
    //   Flying: "#89f",
    //   Psychic: "#f59",
    //   Bug: "#ab2",
    //   Rock: "#ba6",
    //   Ghost: "#66b",
    //   Dragon: "#76e",
    //   Dark: "#754",
    //   Steel: "#aab",
    //   Fairy: "#e9e",
    //   Curse: "#698"
    // };
    return { data };
  },
  actions: {
    async loadRow() {
      this.data = await d3.csvParse('../../data/head.csv');
    }
  }
})