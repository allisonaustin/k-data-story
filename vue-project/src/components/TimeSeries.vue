<script lang="ts">
import * as d3 from "d3";
import { isEmpty, debounce, range } from 'lodash';
import { ComponentSize, Margin } from '../types';
import { StringDecoder } from "string_decoder";

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
                rack: 'l07'
            };
            datum.push(Obj)
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

export default {
    data() {
        return {
            size: { width: 500, height: 500 } as ComponentSize,
            chartSize: { width: 400, height: 250 } as ComponentSize,
            margin: {left: 20, right: 20, top: 20, bottom: 30} as Margin,
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
                .attr('viewBox', [0, 0, this.size.width, this.size.height])
            const tooltip = d3.select('.tooltip')

            const lineColors = ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072']
            const cpus = ['cpu 0', 'cpu 1', 'cpu 2', 'cpu 3']
            const timeParse = d3.timeParse('%Y-%m-%d %H:%M:%S')
            const timeFormat = d3.timeFormat('%H:%M');
            const x = d3.scaleTime()
                .domain(d3.extent(datum, function(d) { return d.check_time }))
                .range([0, 350])

            const y = d3.scaleLinear()
                .domain([0, d3.max(datum, function(d) { return +d.temp })])
                .range([ 250, 0 ])
            
            const chartXAxis = d3.axisBottom(x)
                .tickFormat(timeFormat)
                .ticks(d3.timeMinute.every(15));

            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left}, ${this.size.height - this.margin.bottom})`)
                .call(chartXAxis)
                .selectAll('text')
                .attr('transform', 'rotate(-45)') 
                .style('text-anchor', 'end'); 
            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left}, ${this.size.height - this.margin.bottom - this.chartSize.height})`)
                .call(d3.axisLeft(y))

            const yLabel = chartContainer.append('text')
                .attr('x', this.margin.left + 10)
                .attr('y', this.chartSize.height - this.margin.bottom - 10)
                .attr('text-anchor', 'middle')
                .style('font-size', '12')
                .text('Temp (°C)')

            const chartTitle = chartContainer.append('text')
                .attr('x', this.chartSize.width / 2)
                .attr('y', this.chartSize.height - this.margin.bottom - 30)
                .attr('text-anchor', 'middle')
                .style('font-size', '16')
                .text('Rack L07')

            const linesGroup = chartContainer.append('g');
            
            const lines = Object.keys(temps).forEach(node => {
                const path  = linesGroup.append('path')
                    .datum(temps[node])
                    .attr('fill', 'none')
                    .attr('transform', `translate(${this.margin.left}, ${this.chartSize.height - this.margin.bottom})`) 
                    .attr('stroke', d => lineColors[3])
                    .attr('stroke-width', 1.5)
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
                            .style('left', `${xPos + 630}px`)
                            .style('top', `${yPos + 490}px`)
                            .style('opacity', 1);

                        // highlighting the hovered line
                        path.attr('stroke', 'steelblue')
                            .attr('stroke-opacity', 1)
                            .attr('stroke-width', 5);

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
                            .attr('stroke', d => lineColors[3])
                            .attr('stroke-opacity', 0.9)
                            .attr('stroke-width', 1.5);
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
            
            // let legendX = this.chartSize.width - this.margin.right
            // let legendY = this.chartSize.height - this.margin.bottom
            // let legendSymbolSize = 10
            // let legendItemHeight = 20

            // const legendContainer = chartContainer.append('g')
            //     .attr('class', 'legend-container')
            //     .attr('transform', `translate(${legendX}, ${legendY})`)
            
            // const legendItems = legendContainer.selectAll('.legend-item')
            //     .data(cpus)
            //     .enter()
            //     .append('g')
            //     .attr('class', 'legend-item')
            //     .attr('transform', (d, i) => `translate(0, ${i * legendItemHeight})`)
            
            // legendItems.append('circle')
            //     .attr('cx', this.margin.left)
            //     .attr('cy', 0)
            //     .attr('r', legendSymbolSize / 2)
            //     .attr('fill', (d, i) => lineColors[i]);
            
            // legendItems.append('text')
            //     .attr('x', this.margin.left + legendSymbolSize + 10)
            //     .attr('y', 0)
            //     .attr('dy', '0.35em')
            //     .text(i => i);
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
    height: 500px;
    width: 500px;
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
