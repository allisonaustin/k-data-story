<script lang="ts">
import * as d3 from 'd3';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';

const temp_data_err = await d3.csv('../../data/temp-data-l07.csv');
// const data = await d3.csv('../../data/temp-data-m05.csv');
const rack_err = 'l07'
const bp_err = '0'
const sb_err = '6'


let tempDataErr = temp_data_err.map(d => {
    let Obj = {
        check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
        cpu0: +d[`bp${bp_err}_sb${sb_err}_cpu_0_temp`],
        cpu1: +d[`bp${bp_err}_sb${sb_err}_cpu_1_temp`],
        cpu2: +d[`bp${bp_err}_sb${sb_err}_cpu_2_temp`],
        cpu3: +d[`bp${bp_err}_sb${sb_err}_cpu_3_temp`],

        rack: 'l07'
    }
    return Obj
})

let test = temp_data_err.map(d => {
    let Obj = {
        check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
        rack: rack_err
    }
    Object.keys(d).forEach((c) => {
        if (String(c).includes('temp')) {
            Obj[c] = +d[c]
        }

    })
    return(Obj)
    
})
export default {
    data() {
        return {
            size: { width: 1000, height: 500 } as ComponentSize,
            // size: { width: 0, height: 0 } as ComponentSize,
            margin: {left: 40, right: 25, top: 20, bottom: 20} as Margin,
        } }, 
    computed: {
        rerender() {
            return (!isEmpty(temp_data_err)) && this.size
        }
    },
    created() {
        if (isEmpty(temp_data_err)) return;
        this.initChart()
    },
    methods: {
        onResize() {
            let target = this.$refs.heatmapContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight};
        },
        initChart() {
            // const chart = d3.select('#heatmap-svg')
            const chartContainer = d3.select('#heatmap-svg')
                .attr('viewBox', [0, 0, this.size.width, this.size.height])
            const timeFormat = d3.timeFormat('%H:%M');
            let padding = 60
            let timeBand = tempDataErr[1].check_time - tempDataErr[0].check_time
            let timeExtent = d3.extent(tempDataErr.map(d => d.check_time))
            let cpuList = ["CPU 0", "CPU 1", "CPU 2", "CPU 3"]
            let cpu_list = ["cpu_0", "cpu_1", "cpu_2", "cpu_3"]
            // console.log(timeExtent)

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
            const tooltip = d3.select(".tooltip_heat")
            // .attr("class", "tooltip_heat")
            function mouseover(event, d) {

            }
            let cy = 0
            cpuList.forEach(item => {
                grid.selectAll("heatmap")
                    .data(tempDataErr)
                    .enter()
                    .append('rect')
                        .attr("class", d => 'cpu' + `${cy}` + `${Math.round(xScale(new Date(d.check_time.getTime() - timeBand / 2)))}`)
                        .attr('x', d =>  xScale(new Date(d.check_time.getTime() - timeBand / 2)))
                        .attr('y', yScale(item))
                        .attr('width', 0.98 * xScale(tempDataErr[1].check_time) - xScale(tempDataErr[0].check_time))
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
                    .on('mouseover', function (event, d) {
                        const [xPos, yPos] = d3.pointer(event);
                        // d3.select(this).transition()
                        //     .duration('50')
                        //     .attr('opacity', '.85');
                        d3.selectAll('.' + this.getAttribute('class'))
                            .transition()
                            .duration('50')
                            .attr('opacity', '.85');
                        tooltip.transition()
                            .duration(50)
                            .style("opacity", 1);
                        // let num = (Math.round((d.value / d.data.all) * 100)).toString() + '%';
                        tooltip.html("testing")
                        .style("left", `${event.x}px`)
                        .style("top", `${event.y}px`)
                        // .style("left", `200px`)
                        // .style("top", `200px`)
                    })
                    .on('mouseout', function (event, d) {
                        d3.selectAll('.' + this.getAttribute('class'))
                            .transition()
                            .duration('100')
                            .attr('opacity', '1');
                        tooltip.transition()
                            .duration('100')
                            .style("opacity", 0);
                    });
                cy += 1
            })

            // second chart
            const chartContainerSec = d3.select('#heatmap-svg-nor')
                .attr('viewBox', [0, 0, this.size.width, this.size.height])

            const xAxisSec = chartContainerSec.append('g')
                .attr('transform', `translate(0, ${this.size.height - padding})`)
                .call(xTicks)

            const yAxisSec = chartContainerSec.append('g')
                .attr('transform', `translate(${padding}, 0)`)
                .call(d3.axisLeft(yScale))
            
            // let tempExtents = []
            // tempExtents.push(d3.extent(tempDataErr.map(d => d.cpu0)))
            // tempExtents.push(d3.extent(tempDataErr.map(d => d.cpu1)))
            // tempExtents.push(d3.extent(tempDataErr.map(d => d.cpu2)))
            // // tempExtents.push(d3.extent(tempDataErr.map(d => d.cpu3)))
            // const colorBand = d3.scaleLinear()
            //     .domain([d3.min(tempExtents.map(d => d[0])), d3.max(tempExtents.map(d => d[1]))])
            //     .range(["white", "#69b3a2"])
            
            // heatmap blocks
            let gridSec = chartContainerSec.append('g')
            cy = 0
            cpuList.forEach(item => {
                let cx = 0
                 gridSec.selectAll("heatmap")
                    .data(tempDataErr)
                    .enter()
                    .append('rect')
                    .attr("class", d => 'cpu' + `${cy}` + `${Math.round(xScale(new Date(d.check_time.getTime() - timeBand / 2)))}`)
                        .attr('x', d =>  xScale(new Date(d.check_time.getTime() - timeBand / 2)))
                        .attr('y', yScale(item))
                        .attr('width', 0.98 * xScale(tempDataErr[1].check_time) - xScale(tempDataErr[0].check_time))
                        .attr('height', yScale.bandwidth())
                        .attr('fill', d => {
                            cx += 1
                            if (item == 'CPU 0')
                                return colorBand(d['cpu0'])
                            else if (item == 'CPU 1')
                                return colorBand(d['cpu1'])
                            else if (item == 'CPU 2')
                                return colorBand(d['cpu2'])
                            else
                                return colorBand(d['cpu3'])
                        })
                    .on('mouseover', function (event, d) {
                        const [xPos, yPos] = d3.pointer(event);
                        d3.selectAll('.' + this.getAttribute('class'))
                            .transition()
                            .duration('50')
                            .attr('opacity', '.85');
                        tooltip.transition()
                            .duration(50)
                            .style("opacity", 1);
                        // let num = (Math.round((d.value / d.data.all) * 100)).toString() + '%';
                        tooltip.html("testing")
                        .style("left", `${event.x}px`)
                        .style("top", `${event.y}px`)
                        // .style("left", `200px`)
                        // .style("top", `200px`)
                    })
                    .on('mouseout', function (event, d) {
                        d3.selectAll('.' + this.getAttribute('class'))
                            .transition()
                            .duration('100')
                            .attr('opacity', '1');
                        tooltip.transition()
                            .duration('100')
                            .style("opacity", 0);
                    });
                cy += 1
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
        <!-- <h2>Heatmap Layout</h2> -->
        <svg id="heatmap-svg"></svg>
        <svg id="heatmap-svg-nor"></svg>
        <div class = "tooltip_heat"></div>
    </div>
</template>

<style scoped>
.chartContainer {
    height: 200px;
    width: 200px;
}

.tooltip_heat{
    position: absolute;
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