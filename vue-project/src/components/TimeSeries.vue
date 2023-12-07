<script lang="ts">
import * as d3 from "d3";
import { isEmpty, debounce, range } from 'lodash';
import { ComponentSize, Margin, ContainerRect } from '../types';
import { errorPeriod, errorNode, normalNode } from '../colors';
import { NONAME } from "dns";

const temp_data_err = await d3.csv('../../data/temp-data-l07.csv');
const temp_data_norm = await d3.csv('../../data/temp-data-m05.csv');
const vol_data_err = await d3.csv('../../data/vol-data-l07.csv');
const vol_data_norm = await d3.csv('../../data/vol-data-m05.csv');
const rack_err = 'l7'
const rack_norm = 'm5'
const bp_err = '0'
const sb_err = '6'

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

function loadTempDataErr() {
    let err = [];
    temp_data_err.forEach(d => {
        (Object.keys(d)).forEach((c) => {
            if (String(c).includes('temp')) {
                let Obj = { 
                    check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
                    value: +d[c],
                    node: c,
                    rack: rack_err
                };
                err.push(Obj)
            }
        })
    })
    return err;
}

function loadTempDataNorm() {
    let norm = []
    temp_data_norm.forEach(d => {
        (Object.keys(d)).forEach((c) => {
            if (String(c).includes('temp') && String(c) !== 'in_air' && String(c) !== 'out_air') {
                let Obj = { 
                    check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
                    value: +d[c],
                    node: c,
                    rack: rack_norm
                };
                norm.push(Obj)
            }
        })
    })
    return norm;
}

function loadVoltageDataErr() {
    let err = [];
    vol_data_err.forEach(d => {
        (Object.keys(d)).forEach((c) => {
            if (String(c).includes('vol')) {
                let Obj = { 
                    check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
                    value: +d[c],
                    node: c,
                    rack: rack_err
                };
                err.push(Obj)
            }
        })
    })
    return err;
}

function loadVoltageDataNorm() {
    let norm = []
    vol_data_norm.forEach(d => {
        (Object.keys(d)).forEach((c) => {
            if (String(c).includes('vol')) {
                let Obj = { 
                    check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
                    value: +d[c],
                    node: c,
                    rack: rack_norm
                };
                norm.push(Obj)
            }
        })
    })
    return norm;
}

export default {
    props: {
        dataset: {
            type: String,
            required: true,
        }
    },
    data() {
        return {
            chartId: 1,
            datum: [] as any[],
            datum_n: [] as any[],
            data: [],
            data_n: [],
            y_scale_datum: [] as any[],
            size: { width: 600, height: 600 } as ComponentSize,
            chartSize: { width: 500, height: 400 } as ComponentSize,
            margin: {left: 50, right: 0, top: 20, bottom: 40} as Margin,
            errRack: 'l07',
            normRack: 'm05',
            showErrReadings: true,
            showNormReadings: true,
            selected: null,
        }
    }, 
    computed: {
        rerender() {
            return (!isEmpty(this.dataset)) && this.size
        }
    },
    created() {
        if (isEmpty(this.dataset)) return;
        if (this.dataset == 'temp') {
            this.chartId = 1
            this.datum = loadTempDataErr()
            this.datum_n = loadTempDataNorm()
        } else {
            this.chartId = 2
            this.datum = loadVoltageDataErr()
            this.datum_n = loadVoltageDataNorm()
        }
        this.data = groupBy(this.datum, 'node')
        this.data_n = groupBy(this.datum_n, 'node')
        this.y_scale_datum = this.datum
        this.initChart();
    },
    methods: {
        onResize() {
            let target = this.$refs.chartContainer as HTMLElement
            if (!target) return;
            this.size = { width: target.clientWidth || 0, height: target.clientHeight || 0};
        },
        updateChart() {
            // updating y scale if error readings are hidden
            // if (!this.showErrReadings) {
            //     this.y_scale_datum = this.datum_n;
            // } else {
            //     this.y_scale_datum = this.datum;
            // }

            // if (this.dataset == 'temp') d3.select('#temp-time-series-svg').selectAll('*').remove()
            // else d3.select('#vol-time-series-svg').selectAll('*').remove()
            
            // this.initChart()

            const errLines = d3.select('#err-lines-group' + this.chartId)
            const normLines = d3.select('#lines-group' + this.chartId)

            if (this.showErrReadings) {
                errLines.style('display', 'block')
            } 
            if (!this.showErrReadings) {
                errLines.style('display', 'none')
            }
            if (this.showNormReadings) {
                normLines.style('display', 'block')
            } 
            if (!this.showNormReadings) {
                normLines.style('display', 'none')
            }
        },
        initChart() {
            let chartContainer = this.dataset == 'temp' ? d3.select('#temp-time-series-svg') : d3.select('#vol-time-series-svg')
                
            chartContainer.attr('viewBox', [0, 0, this.chartSize.width, this.chartSize.height])

            const tooltip = d3.select('.tooltip')
            const lineColors = [ normalNode, errorNode ]
            const racks = [ rack_norm, rack_err ]
            const yPadding = 30

            const data = { ...this.data }
            const data_n = { ...this.data_n }

            const tempChartTitle = "Temperature Readings"
            const tempYLabel = "°C"
            const volChartTitle = "Voltage Readings"
            const volYLabel = ""

            const timeParse = d3.timeParse('%Y-%m-%d %H:%M:%S')
            const timeFormat = d3.timeFormat('%H:%M');

            const x = d3.scaleTime()
                .domain(d3.extent(this.datum, function(d) { return d.check_time }))
                .range([0, 370])

            const y = d3.scaleLinear()
                .domain([d3.min(this.y_scale_datum, function(d) { return +d.value }), d3.max(this.y_scale_datum, function(d) { return +d.value })])
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
                .attr('class', 'y-axis')
                .attr('transform', `translate(${this.margin.left}, ${this.margin.bottom + this.margin.top + yPadding})`)
                .call(d3.axisLeft(y))

            const yLabel = chartContainer.append('text')
                .attr('x', this.margin.left)
                .attr('y', this.margin.bottom + this.margin.top + yPadding - 15)
                .attr('text-anchor', 'middle')
                .style('font-size', '10')
                .text(this.dataset == 'temp' ? tempYLabel : volYLabel)

            const chartTitle = chartContainer.append('text')
                .attr('x', this.chartSize.width / 2)
                .attr('y', this.margin.top + this.margin.bottom)
                .attr('text-anchor', 'middle')
                .style('fill', '#333')
                .style('font-style', 'bold')
                .style('font-size', '16')
                .style('font-family', 'Helvetica Neue, sans-serif')
                .text(this.dataset == 'temp' ? tempChartTitle : volChartTitle)

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

            const linesGroup = chartContainer.append('g').attr('id', 'lines-group' + this.chartId);
            const errLinesGroup = chartContainer.append('g').attr('id', 'err-lines-group' + this.chartId);
            let selectedLine = null

            // normal readings
            const norm_lines = Object.keys(data_n).forEach(node => {
                const path  = linesGroup.append('path')
                    .datum(data_n[node])
                    .attr('fill', 'none')
                    .attr('transform', `translate(${this.margin.left}, ${this.margin.bottom + this.margin.top + yPadding})`) 
                    .attr('stroke', normalNode)
                    .attr('stroke-width', 1)
                    .attr('stroke-opacity', 0.9)
                    .attr('d', d3.line()
                        .x(d => x(d.check_time))
                        .y(d => y(d.value))
                    );

                    const dataPoints = linesGroup.selectAll('data-point')
                        .data(data_n[node])
                        .enter()
                        .append('circle')
                        .attr('class', 'data-point')
                        .attr('transform', `translate(${this.margin.left}, ${this.margin.bottom + this.margin.top + yPadding})`) 
                        .attr('cx', d => x(d.check_time))
                        .attr('cy', d => y(d.value))
                        .attr('r', 1.4) 
                        .attr('fill', 'black') 
                        .style('opacity', 0);

                    // tooltip to display node
                    path.on('mouseover', function (event, d) {
                        if (linesGroup.style('display') !== 'none' && selectedLine == null) {
                            const [xPos, yPos] = d3.pointer(event);
                            d3.select(this).style("cursor", "pointer");

                            // showing datapoints 
                            dataPoints
                                .filter(point => data_n[node].some(dataPoint => dataPoint.value === point.value && dataPoint.check_time === point.check_time))
                                .style('opacity', 1);

                            tooltip.transition()
                                .duration(200)
                                .style('opacity', .9);

                            const lineEnd = path.node().getPointAtLength(path.node().getTotalLength());

                            tooltip.html(`${String(node).includes('temp') ? node.slice(0, -5) : node.slice(0, -4)}`) // removing temp/vol from tooltip
                                .style('left', `${lineEnd.x + chartContainer.node().getBoundingClientRect().left}px`)
                                .style('top', `${lineEnd.y + chartContainer.node().getBoundingClientRect().top}px`)
                                .style('opacity', 1);

                            errLinesGroup.selectAll('path')
                                .filter(otherPath => otherPath !== path.node())
                                .attr('stroke', 'lightgray')
                                .attr('stroke-opacity', 0.6);

                            linesGroup.selectAll('path')
                                .filter(otherPath => otherPath !== path.node())
                                .attr('stroke', 'lightgray')
                                .attr('stroke-opacity', 0.6);

                            // highlighting the hovered line
                            path.attr('stroke-opacity', 1)
                                .attr('stroke', normalNode)
                                .attr('stroke-width', 2);
                        }
                    })
                    path.on('mousedown', function () {
                        selectedLine = d3.select(this);
                    })
                    .on('mouseout', function () {
                        if (selectedLine == null) {
                            dataPoints.style('opacity', 0);

                            // hide tooltip
                            tooltip.transition()
                                .duration(500)
                                .style('opacity', 0);
                            // resetting styles for all lines
                            linesGroup.selectAll('path')
                                .attr('stroke', normalNode)
                                .attr('stroke-opacity', 0.9)
                                .attr('stroke-width', 0.9);

                            errLinesGroup.selectAll('path')
                                .attr('stroke', errorNode)
                                .attr('stroke-opacity', 0.9)
                                .attr('stroke-width', 0.9);
                        }
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
            
            // readings containing error node
            const err_lines = Object.keys(data).forEach(node => {
                const path  = errLinesGroup.append('path')
                    .datum(data[node])
                    .attr('fill', 'none')
                    .attr('transform', `translate(${this.margin.left}, ${this.margin.bottom + this.margin.top + yPadding})`) 
                    .attr('stroke', errorNode)
                    .attr('stroke-width', 1)
                    .attr('stroke-opacity', 0.9)
                    .attr('d', d3.line()
                        .x(d => x(d.check_time))
                        .y(d => y(d.value))
                    );

                    const errDataPoints = errLinesGroup.selectAll('data-point')
                        .data(data[node])
                        .enter()
                        .append('circle')
                        .attr('class', 'data-point')
                        .attr('transform', `translate(${this.margin.left}, ${this.margin.bottom + this.margin.top + yPadding})`) 
                        .attr('cx', d => x(d.check_time))
                        .attr('cy', d => y(d.value))
                        .attr('r', 1.4) 
                        .attr('fill', 'black') 
                        .style('opacity', 0);

                    // tooltip to display node
                    path.on('mouseover', function (event, d) {
                        if (linesGroup.style('display') !== 'none' && selectedLine == null) {
                            const [xPos, yPos] = d3.pointer(event);
                            d3.select(this).style("cursor", "pointer");

                            errDataPoints
                                .filter(point => data[node].some(dataPoint => dataPoint.value === point.value && dataPoint.check_time === point.check_time))
                                .style('opacity', 1);
                            
                            tooltip.transition()
                                .duration(200)
                                .style('opacity', .9);

                            const lineEnd = path.node().getPointAtLength(path.node().getTotalLength());
            
                            tooltip.html(`${String(node).includes('temp') ? node.slice(0, -5) : node.slice(0, -4)}`)
                                .style('left', `${lineEnd.x + chartContainer.node().getBoundingClientRect().left}px`)
                                .style('top', `${lineEnd.y + chartContainer.node().getBoundingClientRect().top}px`)
                                .style('opacity', 1);
                        
                            errLinesGroup.selectAll('path')
                                .filter(otherPath => otherPath !== path.node())
                                .attr('stroke', 'lightgray')
                                .attr('stroke-opacity', 0.6);

                            linesGroup.selectAll('path')
                                .filter(otherPath => otherPath !== path.node())
                                .attr('stroke', 'lightgray')
                                .attr('stroke-opacity', 0.6);

                            // highlighting the hovered line
                            path.attr('stroke-opacity', 1)
                                .attr('stroke', errorNode)
                                .attr('stroke-width', 2);
                        }
                    })
                    path.on('mousedown', function () {
                        selectedLine = d3.select(this);
                    })
                    // hide tooltip
                    .on('mouseout', function () {
                        if (selectedLine == null) {
                            errDataPoints.style('opacity', 0);

                            tooltip.transition()
                                .duration(500)
                                .style('opacity', 0);

                            // resetting styles for all lines
                            errLinesGroup.selectAll('path')
                                .attr('stroke', errorNode)
                                .attr('stroke-opacity', 0.9)
                                .attr('stroke-width', 0.9);

                            linesGroup.selectAll('path')
                                .attr('stroke', normalNode)
                                .attr('stroke-opacity', 0.9)
                                .attr('stroke-width', 0.9);
                        }
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

                chartContainer.on('click', function (event) {
                    const clickedElement = event.target;
                    const isLineOrDataPoint = clickedElement.matches('path') || clickedElement.matches('.data-point');
                    if (!isLineOrDataPoint) {
                        let errPoints = errLinesGroup.selectAll('.data-point')
                        let points = linesGroup.selectAll('.data-point')

                        errPoints.style('opacity', 0);
                        points.style('opacity', 0);

                        // hide tooltip
                        tooltip.transition()
                            .duration(500)
                            .style('opacity', 0);

                        // resetting styles for all lines
                        linesGroup.selectAll('path')
                            .attr('stroke', normalNode)
                            .attr('stroke-opacity', 0.9)
                            .attr('stroke-width', 0.9);

                        errLinesGroup.selectAll('path')
                            .attr('stroke', errorNode)
                            .attr('stroke-opacity', 0.9)
                            .attr('stroke-width', 0.9);

                        // Clear the selected line
                        selectedLine = null;
                    }
                });

                // let legendX = this.margin.right + this.chartSize.height - this.margin.bottom
                // let legendY = this.margin.bottom + this.margin.top
                // let legendSymbolSize = 10
                // let legendItemWidth = 20
                // let legendItemHeight = 20

                // const legendContainer = chartContainer.append('g')
                //     .attr('class', 'legend-container')
                //     .attr('transform', `translate(${legendX}, ${legendY})`)
                
                // const legendItems = legendContainer.selectAll('.legend-item')
                //     .data(racks)
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
                //     .attr('x', this.margin.left + legendSymbolSize)
                //     .attr('y', 0)
                //     .attr('dy', '0.35em')
                //     .style('font-size', '10')
                //     .text(i => i);


                // annotating CPU error on first chart
                if (this.dataset == 'temp') {
                    const lineStartX = x(startTime) + this.margin.left + 3;
                    const lineStartY = y(-10);
                    const endX = 0;
                    const endY = 50;
                    const padding = 10;

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
                        .text('CPU error occurs at 14:52:00')
                }
        }
    },
    watch: {
        size(newSize) {
            if (newSize.width > 0 && newSize.height > 0) {
                if (this.dataset == 'temp') d3.select('#temp-time-series-svg').selectAll('*').remove()
                else d3.select('#vol-time-series-svg').selectAll('*').remove()
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
    <div ref="chartContainer" class="container">
        <div v-if="dataset=='temp'">
            <svg id="temp-time-series-svg" ref="timeSeriesTemp"></svg>
            <div class="checkbox-container">
            <label>
                <input type="checkbox" checked v-model="showErrReadings" @change="updateChart" /> {{ errRack }}
            </label>
            <label>
                <input type="checkbox" checked v-model="showNormReadings" @change="updateChart" /> {{ normRack }}
            </label>
        </div>
        </div>
        <div v-else>
            <svg id="vol-time-series-svg" ref="volSeriesTemp"></svg>
            <div class="checkbox-container">
            <label>
                <input type="checkbox" checked v-model="showErrReadings" @change="updateChart" /> {{ errRack }}
            </label>
            <label>
                <input type="checkbox" checked v-model="showNormReadings" @change="updateChart" /> {{ normRack }}
            </label>
        </div>
        </div>
        <div class="tooltip"></div>
    </div>
</template>

<style scoped>
.container {
    height: 600px;
    width: 600px;
}

.legend-item {
  cursor: pointer; 
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

.checkbox-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 12px;
}
</style>
