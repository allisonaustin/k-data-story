<script lang="ts">
import * as d3 from "d3";
import { isEmpty, debounce, range } from 'lodash';
import { ComponentSize, Margin } from '../types';
import { errorPeriod, errorNode, normalNode } from '../colors';
const temp_data_err = await d3.csv('../../data/temp-data-l07.csv');
const temp_data_norm = await d3.csv('../../data/temp-data-m05.csv');
const rack_err = 'l7'
const rack_norm = 'm5'
const bp_err = '0'
const sb_err = '6'

let datum = []
temp_data_err.forEach(d => {
    (Object.keys(d)).forEach((c) => {
        if (String(c).includes('temp')) {
            let Obj = { 
                check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
                temp: +d[c],
                node: c,
                rack: rack_err
            };
            datum.push(Obj)
        }
    })
})

let datum_norm = []
temp_data_norm.forEach(d => {
    (Object.keys(d)).forEach((c) => {
        if (String(c).includes('temp')) {
            let Obj = { 
                check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
                temp: +d[c],
                node: c,
                rack: rack_norm
            };
            datum_norm.push(Obj)
        }
    })
})

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

let temps = groupBy(datum, 'node')
let temps_n = groupBy(datum_norm, 'node')

export default {
    data() {
        return {
            size: { width: 600, height: 600 } as ComponentSize,
            chartSize: { width: 500, height: 400 } as ComponentSize,
            margin: {left: 100, right: 0, top: 20, bottom: 40} as Margin,
        }
    }, 
    computed: {
        rerender() {
            return (!isEmpty(datum)) && this.size
        }
    },
    created() {
        if (isEmpty(datum)) return;
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
                .attr('viewBox', [0, 0, this.chartSize.width, this.chartSize.height])
            const tooltip = d3.select('.tooltip')
            const lineColors = [ normalNode, errorNode ]
            const racks = [ rack_norm, rack_err ]
            const yPadding = 30

            const timeParse = d3.timeParse('%Y-%m-%d %H:%M:%S')
            const timeFormat = d3.timeFormat('%H:%M');
            const x = d3.scaleTime()
                .domain(d3.extent(datum, function(d) { return d.check_time }))
                .range([0, 370])

            const y = d3.scaleLinear()
                .domain([0, d3.max(datum, function(d) { return +d.temp })])
                .range([ 250, 0 ])
            
            const chartXAxis = d3.axisBottom(x)
                .tickFormat(timeFormat)
                .ticks(d3.timeMinute.every(15));

            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left}, ${this.chartSize.height - this.margin.bottom - this.margin.top})`)
                .call(chartXAxis)
                .selectAll('text')
                .attr('transform', 'rotate(-45)') 
                .style('text-anchor', 'end'); 
            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left}, ${this.margin.bottom + this.margin.top + yPadding})`)
                .call(d3.axisLeft(y))

            const xLabel = chartContainer.append('text')
                .attr('x', this.chartSize.width / 1.63)
                .attr('y', this.chartSize.height - this.margin.bottom + this.margin.top)
                .attr('text-anchor', 'middle')
                .style('font-size', '10')
                .text('Time')

            const yLabel = chartContainer.append('text')
                .attr('x', this.margin.left)
                .attr('y', this.margin.bottom + this.margin.top + yPadding - 15)
                .attr('text-anchor', 'middle')
                .style('font-size', '10')
                .text('°C')

            const chartTitle = chartContainer.append('text')
                .attr('x', this.chartSize.width / 1.63)
                .attr('y', this.margin.top + this.margin.bottom)
                .attr('text-anchor', 'middle')
                .style('fill', '#333')
                .style('font-style', 'bold')
                .style('font-size', '16')
                .text('Temperature Readings')

            // CPU error time
            const startTime = new Date("2019-05-28 14:50:00");
            const endTime = new Date("2019-05-28 14:55:00");

            const errorInterval = chartContainer.append('g')
                .append('rect')
                .attr('x', x(startTime) + this.margin.left)
                .attr('y', this.margin.bottom + this.margin.top + yPadding)
                .attr('width', x(endTime) - x(startTime))
                .attr('height', this.chartSize.height - 150)
                .attr('fill', errorPeriod)
                .attr('opacity', 0.3)

            const linesGroup = chartContainer.append('g')
            // normal readings
            const norm_lines = Object.keys(temps_n).forEach(node => {
                const path  = linesGroup.append('path')
                    .datum(temps_n[node])
                    .attr('fill', 'none')
                    .attr('transform', `translate(${this.margin.left}, ${this.margin.bottom + this.margin.top + yPadding})`) 
                    .attr('stroke', normalNode)
                    .attr('stroke-width', 1)
                    .attr('stroke-opacity', 0.9)
                    .attr('d', d3.line()
                        .x(d => x(d.check_time))
                        .y(d => y(d.temp))
                    );

                    // tooltip to display node
                    path.on('mouseover', function (event, d) {
                        const [xPos, yPos] = d3.pointer(event);
                        
                        tooltip.transition()
                            .duration(200)
                            .style('opacity', .9);

                        // node content
                        tooltip.html(`${String(node).includes('temp') ? node.slice(0,-5) : node.slice(0,-4)}`) // removing temp/vol from tooltip
                            .style('left', `${xPos + 830}px`)
                            .style('top', `${yPos + 430}px`)
                            .style('opacity', 1);

                        // highlighting the hovered line
                        path.attr('stroke', 'steelblue')
                            .attr('stroke-opacity', 1)
                            .attr('stroke-width', 3);

                        // not working :(
                        linesGroup.selectAll('path')
                            .filter(otherPath => otherPath !== path.node())
                            .attr('stroke-opacity', 0.6);
                    })
                    // hide tooltip
                    .on('mouseout', function () {
                        tooltip.transition()
                            .duration(500)
                            .style('opacity', 0);

                        // resetting styles for all lines
                        linesGroup.selectAll('path')
                            .attr('stroke', d => normalNode)
                            .attr('stroke-opacity', 0.9)
                            .attr('stroke-width', 0.9);
                    });
                    
                    path.transition()
                        .duration(2000)
                        .on('start', function () {
                            const totalLength = this.getTotalLength();

                            d3.select(this)
                                .attr('stroke-dasharray', `${totalLength} ${totalLength}`)
                                .attr('stroke-dashoffset', totalLength);
                        })
                        .attr('stroke-dashoffset', 0);
                });

            const errLinesGroup = chartContainer.append('g');
            // readings containing error node
            const err_lines = Object.keys(temps).forEach(node => {
                const path  = errLinesGroup.append('path')
                    .datum(temps[node])
                    .attr('fill', 'none')
                    .attr('transform', `translate(${this.margin.left}, ${this.margin.bottom + this.margin.top + yPadding})`) 
                    .attr('stroke', errorNode)
                    .attr('stroke-width', 1)
                    .attr('stroke-opacity', 0.9)
                    .attr('d', d3.line()
                        .x(d => x(d.check_time))
                        .y(d => y(d.temp))
                    );

                    // tooltip to display node
                    path.on('mouseover', function (event, d) {
                        const [xPos, yPos] = d3.pointer(event);
                        
                        tooltip.transition()
                            .duration(200)
                            .style('opacity', .9);

                        // node content
                        tooltip.html(`${String(node).includes('temp') ? node.slice(0,-5) : node.slice(0,-4)}`) // removing temp/vol from tooltip
                            .style('left', `${xPos + 830}px`)
                            .style('top', `${yPos + 430}px`)
                            .style('opacity', 1);

                        // highlighting the hovered line
                        path.attr('stroke', 'steelblue')
                            .attr('stroke-opacity', 1)
                            .attr('stroke-width', 3);

                        // not working :(
                        errLinesGroup.selectAll('path')
                            .filter(otherPath => otherPath !== path.node())
                            .attr('stroke-opacity', 0.6);
                    })
                    // hide tooltip
                    .on('mouseout', function () {
                        tooltip.transition()
                            .duration(500)
                            .style('opacity', 0);

                        // resetting styles for all lines
                        errLinesGroup.selectAll('path')
                            .attr('stroke', d => errorNode)
                            .attr('stroke-opacity', 0.9)
                            .attr('stroke-width', 0.9);
                    });
                    
                    path.transition()
                        .duration(2000)
                        .on('start', function () {
                            const totalLength = this.getTotalLength();

                            d3.select(this)
                                .attr('stroke-dasharray', `${totalLength} ${totalLength}`)
                                .attr('stroke-dashoffset', totalLength);
                        })
                        .attr('stroke-dashoffset', 0);
                });
            
                let legendX = this.margin.right + this.chartSize.height - this.margin.bottom
                let legendY = this.margin.bottom + this.margin.top
                let legendSymbolSize = 10
                let legendItemWidth = 20
                let legendItemHeight = 20

                const legendContainer = chartContainer.append('g')
                    .attr('class', 'legend-container')
                    .attr('transform', `translate(${legendX}, ${legendY})`)
                
                const legendItems = legendContainer.selectAll('.legend-item')
                    .data(racks)
                    .enter()
                    .append('g')
                    .attr('class', 'legend-item')
                    .attr('transform', (d, i) => `translate(0, ${i * legendItemHeight})`)
                
                legendItems.append('circle')
                    .attr('cx', this.margin.left)
                    .attr('cy', 0)
                    .attr('r', legendSymbolSize / 2)
                    .attr('fill', (d, i) => lineColors[i]);
                
                legendItems.append('text')
                    .attr('x', this.margin.left + legendSymbolSize)
                    .attr('y', 0)
                    .attr('dy', '0.35em')
                    .style('font-size', '10')
                    .text(i => i);


                // annotating CPU error on chart
                const lineStartX = x(startTime) + this.margin.left + 3;
                const lineStartY = y(-10);
                const endX = 0;
                const endY = 45;
                const padding = 15;

                const lineEndX = lineStartX - endX; 
                const lineEndY = lineStartY + endY; 

                const line = chartContainer.append('line')
                    .attr('x1', lineStartX)
                    .attr('y1', lineStartY)
                    .attr('x2', lineStartX)
                    .attr('y2', lineStartY)
                    .attr('stroke', 'black') 
                    .attr('stroke-width', 0.8)
                    .transition()
                    .duration(1000)
                    .attr('x2', lineEndX)
                    .attr('y2', lineEndY)

                const errorNote = chartContainer.append('text')
                    .attr('x', lineEndX)
                    .attr('y', lineEndY + padding)
                    .attr('text-anchor', 'middle')
                    .style('font-size', '10')
                    .style('font-style', 'italic')
                    .text('CPU internal error occurs at 14:52:00')
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
    <div ref="tempContainer" class="tempContainer">
        <svg id="time-series-svg"></svg>
        <div class="tooltip"></div>
    </div>
</template>

<style scoped>
.tempContainer {
    height: 600px;
    width: 600px;
}

.legend-item {
  cursor: pointer; 
}

.tooltip {
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
