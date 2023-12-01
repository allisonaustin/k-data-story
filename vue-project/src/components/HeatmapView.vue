<script lang="ts">
import * as d3 from 'd3';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';

const data = await d3.csv('../../data/k_data_processed.csv');
const rack_err = 'l07'
const bp_err = '0'
const sb_err = '6'


let tempData = data.map(d => {
    let Obj = {
        check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
        cpu0: +d[`bp${bp_err}_sb${sb_err}_cpu_0_temp`],
        cpu1: +d[`bp${bp_err}_sb${sb_err}_cpu_1_temp`],
        cpu2: +d[`bp${bp_err}_sb${sb_err}_cpu_2_temp`],
        cpu3: +d[`bp${bp_err}_sb${sb_err}_cpu_3_temp`],

        rack: d.rack
    }
    return Obj
})
let tempDataErr = []
let tempDataNor = []
Object.values(tempData).forEach(d => {
    if (d.rack == rack_err) {
        tempDataErr.push(d)
    }
    else {
        tempDataNor.push(d)
    }
})
export default {
    data() {
        return {
            // size: { width: 1000, height: 500 } as ComponentSize,
            size: { width: 0, height: 0 } as ComponentSize,
            margin: {left: 40, right: 25, top: 20, bottom: 20} as Margin,
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
            let target = this.$refs.heatmapContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight};
        },
        initChart() {
            let chartContainer = d3.select('#heatmap-svg')
                .attr('viewBox', [0, 0, this.size.width, this.size.height])
            const timeFormat = d3.timeFormat('%H:%M');
            let padding = 60
            let timeBand = tempDataErr[1].check_time - tempDataErr[0].check_time
            let timeExtent = d3.extent(tempData.map(d => d.check_time))
            let cpuList = ["CPU 0", "CPU 1", "CPU 2", "CPU 3"]

            let xScale = d3.scaleTime()
                    .domain([new Date(timeExtent[0].getTime() - timeBand / 1.8), new Date(timeExtent[1].getTime() + timeBand / 1.8)])
                    .range([padding, this.size.width - padding])
            let xTicks = d3.axisBottom(xScale)
                .tickFormat(timeFormat)

            let yScale = d3.scaleBand()
                .domain(cpuList)
                .range([padding, this.size.height - padding])
                .padding(0.03)
                // .paddingInner(0.2);

            const xAxis = chartContainer.append('g')
                .attr('transform', `translate(0, ${this.size.height - padding})`)
                .call(xTicks)

            const yAxis = chartContainer.append('g')
                .attr('transform', `translate(${padding}, 0)`)
                .call(d3.axisLeft(yScale))
            
            let tempExtents = []
            tempExtents.push(d3.extent(tempDataErr.map(d => d.cpu0)))
            tempExtents.push(d3.extent(tempDataErr.map(d => d.cpu1)))
            tempExtents.push(d3.extent(tempDataErr.map(d => d.cpu2)))
            tempExtents.push(d3.extent(tempDataErr.map(d => d.cpu3)))
            const colorBand = d3.scaleLinear()
                .domain([d3.min(tempExtents.map(d => d[0])), d3.max(tempExtents.map(d => d[1]))])
                .range(["white", "#69b3a2"])
            
            // heatmap blocks
            let grid = chartContainer.append('g')
                    
            cpuList.forEach(item => {
                 grid.selectAll()
                    .data(tempDataErr)
                    .enter()
                    .append('rect')
                    .attr('x', d =>  xScale(new Date(d.check_time.getTime() - timeBand / 2)))
                    .attr('y', yScale(item))
                    .attr('width', 0.98 * xScale(tempData[2].check_time) - xScale(tempData[0].check_time))
                    .attr('height', yScale.bandwidth())
                    .attr('fill', d => {
                        if (item == 'CPU 0')
                            return colorBand(d['cpu0'])
                        else if (item == 'CPU 1')
                            return colorBand(d['cpu1'])
                        else if (item == 'CPU 2')
                            return colorBand(d['cpu2'])
                        else
                            return colorBand(d['cpu3'])
                    })
            })
                
            // rack grid
        //     const grid = chartContainer.append('g')
        //         .selectAll('rect')
        //         .data(rack_letters.flatMap(letter => rack_nums.map(num => ({ letter, num: String(num) }))))
        //         .enter()
        //         .append('rect')
        //         .attr('x', d => xScale(d.letter))
        //         .attr('y', d => yScale(String(d.num)))
        //         .attr('width', xScale.bandwidth())
        //         .attr('height', yScale.bandwidth())
        //         .attr('fill', d => (d.letter + d.num == rack_err ? '#f88379' : 'lightgray'))
        //         .attr('stroke', 'white')

        //     const lineStartX = xScale(rack_err[0]) + xScale.bandwidth() / 2;
        //     const lineStartY = yScale(rack_err[1]) + yScale.bandwidth() / 2;

        //     const lineEndX = lineStartX + this.size.width / 2; 
        //     const lineEndY = lineStartY; 

        //     const line = chartContainer.append('line')
        //         .attr('x1', lineStartX)
        //         .attr('y1', lineStartY)
        //         .attr('x2', lineStartX)
        //         .attr('y2', lineStartY)
        //         .attr('stroke', 'gray') 
        //         .attr('stroke-width', 1.5)
        //         .transition()
        //         .duration(1000)
        //         .attr('x2', lineEndX)
        //         .attr('y2', lineEndY)
        }
            
    },
    watch: {
        size(newSize) {
            if (newSize.width > 0 && newSize.height > 0) {
                d3.select('#heatmap-svg').selectAll('*').remove()
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
    <div ref="heatmapContainer" class="chartContainer">
        <svg id="heatmap-svg">
        </svg>
    </div>
</template>

<style scoped>
.chartContainer {
    height: 500px;
    width: 1000px;
}
</style>