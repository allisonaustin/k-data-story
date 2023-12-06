<script lang="ts">
import * as d3 from 'd3';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';

const temp_data_err = await d3.csv('../../data/temp-data-l07.csv');
const temp_data_nor = await d3.csv('../../data/temp-data-m05.csv');
const vol_data_err = await d3.csv('../../data/vol-data-l07.csv');
const vol_data_nor = await d3.csv('../../data/vol-data-m05.csv');

const rack_err = 'l07'
const rack_nor = 'm05'
const bp_err = 0
const sb_err = 6
const errTime = new Date("2019-05-28 14:52:00")
function data_group(inputTable, node: string, type: string) {
    let return_table_bf = []
    let return_table_af = []
    inputTable.forEach((d, i) => {
        let Obj = {
            check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
            time_idx: type + i,
            rack: node
        }
        Object.keys(d).forEach((c) => {
            if (String(c).includes(type)) {
                Obj[c] = +d[c]
            }
        })
        if (Obj['check_time'] < errTime){
            return_table_bf.push(Obj)
        }
        else {
            return_table_af.push(Obj)
        }
    })
    return [return_table_bf, return_table_af]
}
let temp_table_err = data_group(temp_data_err, rack_err, 'temp')
let temp_table_err_bf = temp_table_err[0]
let temp_table_err_af = temp_table_err[1]
let temp_table_nor = data_group(temp_data_nor, rack_nor, 'temp')
let temp_table_nor_bf = temp_table_nor[0]
let temp_table_nor_af = temp_table_nor[1]
let vol_table_err = data_group(vol_data_err, rack_err, 'vol')
let vol_table_err_bf = vol_table_err[0]
let vol_table_err_af = vol_table_err[1]
let vol_table_nor = data_group(vol_data_nor, rack_nor, 'vol')
let vol_table_nor_bf = vol_table_nor[0]
let vol_table_nor_af = vol_table_nor[1]

export default {
    props: {
        dataset: {
            type: String,
            required: true,
        }
    },
    data() {
        return {
            size: { width: 800, height: 500 } as ComponentSize,
            svgSize: { width: 760, height: 100 } as ComponentSize,
            svgSizeBf: { width: 245, height: 100 } as ComponentSize,
            svgSizeAf: { width: 720, height: 100 } as ComponentSize,
            colorbarSize: {width: 250, height: 10} as ComponentSize,
            margin: {left: 40, right: 10, top:0, bottom: 20} as Margin,
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
            const timeFormat = d3.timeFormat('%H:%M');
            let timeBand = temp_table_err_bf[1].check_time - temp_table_err_bf[0].check_time
            // let timeExtent = d3.extent(temp_table_err_bf.map(d => d.check_time))
            let cpuList = ["CPU 0", "CPU 1", "CPU 2", "CPU 3"]
            let ibcList = ["IBC 0", "IBC 1", "IBC 2", "IBC 3"]
            let temp_extent = [14, 22]
            const colorBandTemp = d3.scaleSequential(["white", "red"]).domain(temp_extent)
            let vol_extent = [12, 12.5]
            const colorBandVol= d3.scaleSequential(["white", "blue"]).domain(vol_extent)
            
            // tooltip event
            let tooltip = d3.select(".tooltip-heat")
            function mouseover(event, item, info) {
                tooltip.transition()
                    .duration(100)
                    .style("opacity", 1);
                
                tooltip.html(`${item} bp${bp_err} sb${sb_err} ${info}`)
                    .style("left", `${event.x}px`)
                    .style("top", `${event.y+1000}px`)
            }
            function mouseout(event, d) {
                tooltip.transition()
                    .duration(100)
                    .style("opacity", 0);
            }
            
            function chart_init(chart_container: SVGAElement, 
                para, bp: number, sb: number, table_data, dataset = 'temp', before = true, 
                show_cpu = true, show_time = true) {
                let timeExtent = d3.extent(table_data.map(d => d.check_time))
                let svgSize = para.svgSizeAf
                if (before) {
                    svgSize = para.svgSizeBf
                }
                
                let xScale = d3.scaleTime()
                    .domain([new Date(timeExtent[0].getTime() - timeBand / 1.8), new Date(timeExtent[1].getTime() + timeBand / 1.8)])
                    .range([0, svgSize.width - para.margin.left - para.margin.right])

                let xTicks = d3.axisBottom(xScale)
                    .tickFormat(timeFormat)
                    .ticks(d3.timeMinute.every(15))
                    // .tickSize(0)

               
                if (show_time) {
                    const xAxis = chart_container.append('g')
                    if (!show_cpu) {
                        xAxis.attr('transform', `translate(${0}, ${para.margin.top + svgSize.height - para.margin.bottom - para.margin.top})`)
                    }
                    else {
                        xAxis.attr('transform', `translate(${para.margin.left}, ${para.margin.top + svgSize.height - para.margin.bottom - para.margin.top})`)
                    }
                    xAxis 
                        .call(xTicks)
                }
                let yScale = d3.scaleBand()
                    .domain([0, 1, 2, 3])
                    .range([0, svgSize.height - para.margin.bottom - para.margin.top])
                    .padding(0.1)
                    .paddingInner(0.2);
                
                if (show_cpu) {
                    const yTicks = d3.axisLeft(yScale)
                        .tickFormat((d) => {
                            if (dataset == 'temp') {
                                return cpuList[d]
                            }
                            if (dataset == 'vol') {
                                return ibcList[d]
                            }

                        })
                        .tickSize(0)
                    const yAxis = chart_container.append('g')
                        .attr('transform', `translate(${para.margin.left}, ${para.margin.top})`)
                        .call(yTicks).style("stroke-width", "1px")
                }
                

                let grid = chart_container.append('g')
                    
                if (!show_cpu) {
                    grid.attr("transform", `translate(${0}, ${para.margin.top})`)
                }
                else {
                    grid.attr("transform", `translate(${para.margin.left}, ${para.margin.top})`)
                }
                for (let index = 0; index < 4; index ++){
                    grid.selectAll()
                        .data(table_data)
                        .enter()
                        .append('rect')
                            .attr("class", d => {
                                return `t_${d.time_idx}_${index}`
                            })
                            .attr('x', d =>  xScale(new Date(d.check_time.getTime()) - timeBand / 2))
                            .attr('y', () => {
                                if (dataset == 'temp'){
                                    return yScale(index)
                                }
                                else {
                                    return yScale(index)
                                }
                            })
                            .attr('width', 0.98 * xScale(table_data[1].check_time) - xScale(table_data[0].check_time))
                            .attr('height', yScale.bandwidth())
                            .attr('fill', d => {
                                if (dataset == 'temp') {
                                    return colorBandTemp(d[`bp${bp}_sb${sb}_cpu_${index}_temp`])
                                }
                                else {
                                    return colorBandVol(d[`bp${bp}_sb${sb}_ibc_${index}_vol`])
                                }
                                    
                            })
                        .on('mouseover', function (event, d) {
                            d3.selectAll('.' + this.getAttribute('class'))
                                .transition()
                                .duration(100)
                                .attr('opacity', 0.85);
                            if (dataset == 'temp') {
                                mouseover(event, `CPU ${index}`, `${d[`bp${bp}_sb${sb}_cpu_${index}_temp`]} °C`)
                            }
                            else {
                                mouseover(event, `IBC ${index}`, `${d[`bp${bp}_sb${sb}_ibc_${index}_vol`]} V`)
                            }
                            
                        })
                        .on('mouseout', function (event, d) {
                            d3.selectAll('.' + this.getAttribute('class'))
                                .transition()
                                .duration(100)
                                .attr('opacity', '1');
                            mouseout(event, d)
                        });
                }   
                
            }
            // temp
            const colorbar = d3.select("#temp-colorbar")
            let defs = colorbar.append("defs")
            let linearGradient = defs.append("linearGradient")
                .attr("id", "linear-gradient");
            //Set the color for the start (0%)
            linearGradient.selectAll("stop")
                .data(colorBandTemp.ticks().map((t, i, n) => ({ offset: `${100*i/n.length}%`, color: colorBandTemp(t) })))    
                .enter()
                .append("stop")
                .attr("offset", d => d.offset)
                .attr("stop-color", d => d.color);
            
            let rect = colorbar.append('rect')
                .attr('x', this.margin.left)
                .attr('y', 0)
                .attr('width', this.colorbarSize.width - this.margin.left - this.margin.right)
                .attr('height', this.colorbarSize.height)
                .style("fill", "url(#linear-gradient)");

            const colorAxisScale = d3.scaleLinear()
                .domain(colorBandTemp.domain())
                .range([this.margin.left, this.colorbarSize.width - this.margin.right])
            
            const colorAxisTicks = d3.axisBottom(colorAxisScale)
                .ticks(4) 
                .tickSize(-this.colorbarSize.height)
            const colorAxis = colorbar.append("g")
            .attr('transform', `translate(${0}, ${this.colorbarSize.height})`)
            .call(colorAxisTicks)

            const chartContainer = d3.select('#heatmap-svg')
                .attr('viewBox', [0, 0, this.svgSizeBf.width, this.svgSizeBf.height])                
            chart_init(chartContainer, this, bp_err, sb_err, temp_table_err_bf, 'temp', true, true, false)

            const chartContainer_af = d3.select('#heatmap-svg-af')
                .attr('viewBox', [0, 0, this.svgSizeAf.width, this.svgSizeAf.height])
            chart_init(chartContainer_af, this, bp_err, sb_err, temp_table_err_af, 'temp', false, false, false)

            const chartContainerNor_bf = d3.select('#heatmap-svg-nor')
                .attr('viewBox', [0, 0, this.svgSizeBf.width, this.svgSizeBf.height])
            chart_init(chartContainerNor_bf, this, bp_err, sb_err, temp_table_nor_bf, 'temp', true)
            const chartContainerNor_af = d3.select('#heatmap-svg-nor-af')
                .attr('viewBox', [0, 0, this.svgSizeAf.width, this.svgSizeAf.height])
            chart_init(chartContainerNor_af, this, bp_err, sb_err, temp_table_nor_af, 'temp', false, false, true)
            
            // voltage
            const colorbarVol = d3.select("#vol-colorbar")
            let defsVol = colorbarVol.append("defs")
            let linearGradientVol = defsVol.append("linearGradient")
                .attr("id", "linear-gradient-vol");

            linearGradientVol.selectAll("stop")
                .data(colorBandVol.ticks().map((t, i, n) => ({ offset: `${100*i/n.length}%`, color: colorBandVol(t) })))    
                .enter()
                .append("stop")
                .attr("offset", d => d.offset)
                .attr("stop-color", d => d.color);
            
            let rectVol = colorbarVol.append('rect')
                .attr('x', this.margin.left)
                .attr('y', 0)
                .attr('width', this.colorbarSize.width - this.margin.left - this.margin.right)
                .attr('height', this.colorbarSize.height)
                .style("fill", "url(#linear-gradient-vol)");

            const colorAxisScaleVol = d3.scaleLinear()
                .domain(colorBandVol.domain())
                .range([this.margin.left, this.colorbarSize.width - this.margin.right])
            
            const colorAxisTicksVol = d3.axisBottom(colorAxisScaleVol)
                .ticks(4) 
                .tickSize(-this.colorbarSize.height)
            const colorAxisVol = colorbarVol.append("g")
            .attr('transform', `translate(${0}, ${this.colorbarSize.height})`)
            .call(colorAxisTicksVol)


            const chartContainerVol = d3.select('#heatmap-svg-vol')
                .attr('viewBox', [0, 0, this.svgSizeBf.width, this.svgSizeBf.height])                
            chart_init(chartContainerVol, this, bp_err, sb_err, vol_table_err_bf, 'vol', true, true, false)

            const chartContainerVol_af = d3.select('#heatmap-svg-vol-af')
                .attr('viewBox', [0, 0, this.svgSizeAf.width, this.svgSizeAf.height])
            chart_init(chartContainerVol_af, this, bp_err, sb_err, vol_table_err_af, 'vol', false, false, false)

            const chartContainerNorVol_bf = d3.select('#heatmap-svg-vol-nor')
                .attr('viewBox', [0, 0, this.svgSizeBf.width, this.svgSizeBf.height])
            chart_init(chartContainerNorVol_bf, this, bp_err, sb_err, vol_table_nor_bf, 'vol', true)
            const chartContainerNorVol_af = d3.select('#heatmap-svg-vol-nor-af')
                .attr('viewBox', [0, 0, this.svgSizeAf.width, this.svgSizeAf.height])
            chart_init(chartContainerNorVol_af, this, bp_err, sb_err, vol_table_nor_af, 'vol', false, false, true)
            
    
                
        }
    },
    watch: {
        size(newSize) {
            if (newSize.width > 0 && newSize.height > 0) {
                d3.select('#heatmap-svg').selectAll('*').remove()
                // d3.select('#heatmap-svg-nor').selectAll('*').remove()
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
    <div ref="heatmapContainer" class="heatmapContainer">
        <div v-if="dataset == 'temp'" id = "root">
            <svg id="temp-colorbar" class = "colorbar-container"></svg>
            <div>
                <svg id="heatmap-svg" class = "svg-container-bf"></svg>
                <svg id="heatmap-svg-af" class = "svg-container-af"></svg>
                <svg id="heatmap-svg-nor" class = "svg-container-bf"></svg>
                <svg id="heatmap-svg-nor-af" class = "svg-container-af"></svg>
            </div>
            
        </div>
        <div v-else>
            <svg id="vol-colorbar" class = "colorbar-container"></svg>
            <div>
                <svg id="heatmap-svg-vol" class = "svg-container-bf"></svg>
                <svg id="heatmap-svg-vol-af" class = "svg-container-af"></svg>
                <svg id="heatmap-svg-vol-nor" class = "svg-container-bf"></svg>
                <svg id="heatmap-svg-vol-nor-af" class = "svg-container-af"></svg>
            </div>
            
        </div>
        
        <div class = "tooltip-heat">
        </div>        
    </div>
</template>

<style scoped>
.heatmapContainer {
    height: 250px;
    width: 1050px;
}
.svg-container-bf {
    height: 105px;
    width: 255px; 
}
.svg-container-af {
    height: 105px;
    width: 730px; 
}
.colorbar-container {
    height: 20px;
    width: 250px; 
}
.tooltip-heat{
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