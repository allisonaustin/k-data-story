<script lang="ts">
import * as d3 from 'd3';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';

const temp_data_err = await d3.csv('../../data/temp-data-l07.csv');
const temp_data_nor = await d3.csv('../../data/temp-data-m05.csv');

const rack_err = 'l07'
const rack_nor = 'm05'
const bp_err = 0
const sb_err = 6
const errTime = new Date("2019-05-28 14:52:00")
let temp_table_err_bf = []
let temp_table_err_af = []
temp_data_err.forEach((d, i) => {
    let Obj = {
        check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
        time_idx: i,
        rack: rack_err
    }
    Object.keys(d).forEach((c) => {
        if (String(c).includes('temp')) {
            Obj[c] = +d[c]
        }
    })
    if (Obj['check_time'] < errTime){
        temp_table_err_bf.push(Obj)
    }
    else {
        temp_table_err_af.push(Obj)
    }
})
let temp_table_nor_bf = []
let temp_table_nor_af = []
temp_data_nor.forEach((d, i) => {
    let Obj = {
        check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
        time_idx: i,
        rack: rack_nor
    }
    Object.keys(d).forEach((c) => {
        if (String(c).includes('temp')) {
            Obj[c] = +d[c]
        }

    })

    if (Obj['check_time'] < errTime){
        temp_table_nor_bf.push(Obj)
    }
    else {
        temp_table_nor_af.push(Obj)
    }
    
})
export default {
    data() {
        return {
            size: { width: 800, height: 500 } as ComponentSize,
            svgSize: { width: 760, height: 100 } as ComponentSize,
            svgSizeBf: { width: 245, height: 100 } as ComponentSize,
            svgSizeAf: { width: 720, height: 100 } as ComponentSize,
            margin: {left: 40, right: 10, top:0, bottom: 0} as Margin,
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
            
            let extent = [14, 28]
            const colorBand = d3.scaleLinear()
                .domain(extent)
                .range(["white", "black"])
            
            // tooltip event
            let tooltip = d3.select(".tooltip-heat")
            function mouseover(event, item) {
                tooltip.transition()
                    .duration(100)
                    .style("opacity", 1);
                console.log(d3.select("#main-container").property("offsetHeight"))
                tooltip.html(`${item} bp ${bp_err} sb ${sb_err}`)
                    .style("left", `${event.x}px`)
                    .style("top", `${event.y+1000}px`)
            }
            function mouseout(event, d) {
                tooltip.transition()
                            .duration('100')
                            .style("opacity", 0);
            }
            
            function chart_init(chart_container: SVGAElement, 
                para, bp: number, sb: number, table_data, before = true, 
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
                    .tickSize(0)

                let yScale = d3.scaleBand()
                    .domain(cpuList)
                    .range([0, svgSize.height - para.margin.bottom - para.margin.top])

                let yTicks = d3.axisLeft(yScale).tickSize(0)

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
                        .selectAll('text')
                        .attr('transform', 'rotate(-45)') 
                        .style('text-anchor', 'end') 
                }
                if (show_cpu) {
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
                cpuList.forEach((item, index) => {
                    grid.selectAll()
                        .data(table_data)
                        .enter()
                        .append('rect')
                            .attr("class", d => `t_${d.time_idx}_cpu_${index}`)
                            .attr('x', d =>  xScale(new Date(d.check_time.getTime()) - timeBand / 2))
                            .attr('y', yScale(item))
                            .attr('width', 0.98 * xScale(table_data[1].check_time) - xScale(table_data[0].check_time))
                            .attr('height', yScale.bandwidth())
                            .attr('fill', d => {
                                    return colorBand(d[`bp${bp}_sb${sb}_cpu_${index}_temp`])
                            })
                        .on('mouseover', function (event, d) {
                            d3.selectAll('.' + this.getAttribute('class'))
                                .transition()
                                .duration(100)
                                .attr('opacity', 0.85);
                            mouseover(event, item)
                        })
                        .on('mouseout', function (event, d) {
                            d3.selectAll('.' + this.getAttribute('class'))
                                .transition()
                                .duration('100')
                                .attr('opacity', '1');
                            mouseout(event, d)
                        });
                })
                
            }
            const chartContainer = d3.select('#heatmap-svg')
                .attr('viewBox', [0, 0, this.svgSizeBf.width, this.svgSizeBf.height])                
            chart_init(chartContainer, this, bp_err, sb_err, temp_table_err_bf, true, true, false)

            const chartContainer_af = d3.select('#heatmap-svg-af')
                .attr('viewBox', [0, 0, this.svgSizeAf.width, this.svgSizeAf.height])
            chart_init(chartContainer_af, this, bp_err, sb_err, temp_table_err_af, false, false, false)

            const chartContainerNor_bf = d3.select('#heatmap-svg-nor')
                .attr('viewBox', [0, 0, this.svgSizeBf.width, this.svgSizeBf.height])
            chart_init(chartContainerNor_bf, this, bp_err, sb_err, temp_table_nor_bf, true)
            const chartContainerNor_af = d3.select('#heatmap-svg-nor-af')
                .attr('viewBox', [0, 0, this.svgSizeAf.width, this.svgSizeAf.height])
            chart_init(chartContainerNor_af, this, bp_err, sb_err, temp_table_nor_af, false, false, true)
            
    
                
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
        <!-- <h2>Heatmap Layout</h2> -->
        <v-row>
            <h3 id = "paragraph-bf">Before the error occurs</h3> 
            <h3 id = "paragraph-af">After the error occurs</h3> 

        </v-row>
        <v-col id = "root">
            <svg id="heatmap-svg" class = "svg-container-bf"></svg>
            <svg id="heatmap-svg-af" class = "svg-container-af"></svg>
            
        </v-col>
        <v-col>
            <!-- <svg id="heatmap-svg"></svg> -->
            <svg id="heatmap-svg-nor" class = "svg-container-bf"></svg>
            <svg id="heatmap-svg-nor-af" class = "svg-container-af"></svg>
        </v-col>
        <div class = "tooltip-heat">
        </div>        
    </div>
</template>

<style scoped>
.heatmapContainer {
    height: 1000px;
    width: 1050px;
}
.svg-container-bf {
    height: 102px;
    width: 255px; 
}
.svg-container-af {
    height: 102px;
    width: 730px; 
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