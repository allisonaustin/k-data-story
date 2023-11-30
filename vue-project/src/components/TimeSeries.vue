<script lang="ts">
import * as d3 from "d3";
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';

const data = await d3.csv('../../data/k_data_processed.csv');
const rack_err = 'l7'
const bp_err = '0'
const sb_err = '6'

// let tempData = []
// Object.values(data).forEach(d => {
//     let dataObj = {
//         check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
//         temp: +d[`bp${bp_err}_sb${sb_err}_cpu_0_temp`]
//     }
//     tempData.push(dataObj)
// })
let tempData = data.map(d => {
    let Obj = {
        check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
        temp: +d[`bp${bp_err}_sb${sb_err}_cpu_0_temp`],
        rack: d.rack
    }
    return Obj
})

export default {
    data() {
        return {
            size: { width: 300, height: 300 } as ComponentSize,
            margin: {left: 20, right: 20, top: 20, bottom: 20} as Margin,
        }
    }, 
    computed: {
        rerender() {
            return (!isEmpty(data)) && this.size
        }
    },
    created() {
        if (isEmpty(data)) return;
        this.initChart()
    },
    methods: {
        onResize() {
            let target = this.$refs.tempContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight};
        },
        initChart() {
            let chartContainer = d3.select('#time-series-svg')
                .attr('viewBox', [0, 0, this.size.width, this.size.height])

            const timeFormat = d3.timeFormat('%H:%M');
            const x = d3.scaleTime()
                .domain(d3.extent(tempData, function(d) { return d.check_time }))
                .range([0, 250])

            const y = d3.scaleLinear()
                .domain([0, d3.max(tempData, function(d) { return +d.temp })])
                .range([ 250, 0 ])
            
            const chartXAxis = d3.axisBottom(x)
                .tickFormat(timeFormat)
                .ticks(d3.timeMinute.every(15));

            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left}, ${this.size.height - this.margin.left})`)
                .call(chartXAxis)
            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left}, ${this.size.height / 2 - this.margin.bottom})`)
                .call(d3.axisLeft(y))

            const chartTitle = chartContainer.append('text')
                .attr('x', this.margin.left + 10)
                .attr('y', this.size.height / 2 - this.margin.bottom - 10)
                .attr('text-anchor', 'middle')
                .style('font-size', '12')
                .text('CPU Temp')

            const tempLine = chartContainer.append('path')
                .datum(tempData)
                .attr('fill', 'none')
                .attr('stroke', 'green')
                .attr('stroke-width', 1.5)
                .attr('transform', `translate(${this.margin.left}, ${this.size.height / 2 - this.margin.bottom})`) 
                .attr('d', d3.line()
                    .x(d => x(d.check_time))
                    .y(d => y(d.temp))
                )
        }
    },
    watch: {
        size(newSize) {
            if (newSize.width > 0 && newSize.height > 0) {
                d3.select('#time-series-svg').selectAll('*').remove()
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
    <div ref="tempContainer" class="chartContainer">
        <svg id="time-series-svg">
        </svg>
    </div>
</template>

<style scoped>
.chartContainer {
    height: 500px;
    width: 300px;
}
</style>
