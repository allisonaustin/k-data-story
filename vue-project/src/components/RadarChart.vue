<script lang="ts">
import * as d3 from "d3";
import { isEmpty, debounce, range } from 'lodash';
import { ComponentSize, Margin, ContainerRect } from '../types';
import { errorPeriod, errorNode, normalNode } from '../colors';

const csvData = await d3.csv('../../data/head.csv');

const rack_err = 'l7'
const err_x = 18
const err_y = 2
const rack_norm = 'm5'

function groupBy(arr, property) {
    return arr.reduce(function (acc, obj) {
        let key = obj[property]
        if (!acc[key]) {
            acc[key] = []
        }
        acc[key].push(obj)
            return acc
        }, 
    {})
}

let datum = [];
csvData.forEach(d => {
    let Obj = {
        rack: d.rack,
        values: [
            { axis: "pressure_0", value: +d.pressure_0 },
            { axis: "pressure_1", value: +d.pressure_1 },
            { axis: "distance", value: ((+d.x - err_x) ** 2 + (+d.y - err_y) ** 2) ** 0.5 }, // distance from error rack
            { axis: "a1_fan1_rpm", value: +d.a1_fan1_rpm }
        ]
    }
    datum.push(Obj)
})

export default {
    data() {
        return {
            size: { width: 0, height: 0 } as ComponentSize,
            margin: {left: 30, right: 20, top: 20, bottom: 60} as Margin,
        }
    }, 
    computed: {
        rerender() {
            return (!isEmpty(datum)) && this.size
        }
    },
    created() {
        if (isEmpty(datum)) return;
        this.initChart();
    },
    methods: {
        onResize() {
            let target = this.$refs.radarChartContainer as HTMLElement
            if (!target) return;
            this.size = { width: target.clientWidth, height: target.clientHeight};
        },
        updateChart() {
            return;
        },
        initChart() {
            let chartContainer = d3.select('#radar-svg')
                .attr('width', this.size.width)
                .attr('height', this.size.height)                
                .attr('viewBox', [0, 0, this.size.width, this.size.height])
            
            const tooltip = d3.select('.tooltip')
            const numAxes = datum[0].values.length;
            const angleSlice = (Math.PI * 2) / numAxes;

            const colors = d3.scaleOrdinal(d3.schemeAccent)

            let radius = Number(d3.min([this.size.width, this.size.height])) / 3
            let origin = [this.size.width / 2, this.size.height / 2]
            
            const radScale = d3.scaleLinear()
                .domain([0, d3.max(datum[0].values, d => d.value)])
                .range([0, Math.min(this.size.width / 2, this.size.height / 2)]);
            
            let group = chartContainer.append('g')
                .attr(`transform`, `translate(${this.margin.left}, ${this.margin.top})`)
            
            const keys = datum[0].values.map(d => d.axis);
            let radian = 2 * Math.PI / numAxes
            let theta = - Math.PI
            let thetaList = [] as number[]
            for (let i = 0; i < numAxes; i++) {
                thetaList.push(theta)
                theta += radian
            }
            
            const axes = group.selectAll('allLines')
                .data(keys)
                .enter()
                .append('polyline')
                .attr('stroke', 'grey')
                .attr('fill', 'none')
                .attr('stroke-width', 0.5)
                .attr('points', (d, i) => {
                    let p = [origin[0] + radius * Math.cos(thetaList[i]), origin[1] + radius * Math.sin(thetaList[i])]
                    return[origin, p]
                })

            let r = [0, radius / 4, 2 * radius / 4, 3 * radius / 4, radius]

            const backPoly = group.selectAll("allBack")
                .data(r)
                .enter()
                .append('polygon')
                .attr("stroke", "grey")
                .attr('fill', 'none')
                .attr('stroke-width', 0.5)
                .attr('points', (d) => {
                    let point_list = [] 
                    for (let j = 0; j < numAxes; j++) {
                        let r = d
                        let x = origin[0] + r * Math.cos(thetaList[j])
                        let y = origin[1] + r * Math.sin(thetaList[j])
                        point_list.push([x, y])
                    }
                    return point_list
            })

            let rScale = d3.scaleLinear()
                .rangeRound([0, radius])
                .domain([40, 160])

            // axis labels
            const axisLabels = axes.append('text')
                .attr('x', (d, i) => radScale(1.1) * Math.cos(angleSlice * i - Math.PI / 2))
                .attr("y", (d, i) => radScale(1.1) * Math.sin(angleSlice * i - Math.PI / 2))
                .text(d => d.axis)
                .attr('class', 'axis-label');
        },
    },
    watch: {
        size(newSize) {
            if (newSize.width > 0 && newSize.height > 0) {
                d3.select('#radar-svg').selectAll('*').remove()
                this.initChart()
            }
        }
    },
    mounted() {
        window.addEventListener('resize', this.onResize) 
        this.onResize()
    },
    beforeDestroy() {
       window.removeEventListener('resize', this.onResize)
    }
}
</script>
<template>
    <div ref="radarChartContainer" class="container d-flex">
        <svg id="radar-svg" width="100%" height="100%"></svg>
        <div class="tooltip"></div>
    </div>
</template>

<style scoped>
.container {
    height: 600px;
    width: 800px;
}

.tooltip {
    line-height: 1;
    font-weight: bold;
    padding: 10px;
    background: rgba(0, 0, 0, 0.8);
    color: #fff;
    border-radius: 2px;
    font-size: 12px;
    text-align: left;
    opacity: 0;
}
</style>
