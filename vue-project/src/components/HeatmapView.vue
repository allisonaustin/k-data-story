<script lang="ts">
import * as d3 from 'd3';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';

const temp_data_err = await d3.csv('../../processed_data/temp-data-l07.csv');
const temp_data_nor = await d3.csv('../../processed_data/temp-data-m05.csv');
const vol_data_err = await d3.csv('../../processed_data/vol-data-l07.csv');
const vol_data_nor = await d3.csv('../../processed_data/vol-data-m05.csv');

const rack_err = 'l07'
const rack_nor = 'm05'
const bp_err = 0
const sb_err = 6
let bp_select = 0
let sb_select = 0
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
// let temp_table_nor = data_group(temp_data_nor, rack_nor, 'temp')
// let temp_table_nor_bf = temp_table_nor[0]
// let temp_table_nor_af = temp_table_nor[1]
// let vol_table_err = data_group(vol_data_err, rack_err, 'vol')
// let vol_table_err_bf = vol_table_err[0]
// let vol_table_err_af = vol_table_err[1]
// let vol_table_nor = data_group(vol_data_nor, rack_nor, 'vol')
// let vol_table_nor_bf = vol_table_nor[0]
// let vol_table_nor_af = vol_table_nor[1]

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
            svgSizeBf: { width: 145, height: 100 } as ComponentSize,
            svgSizeAf: { width: 400, height: 100 } as ComponentSize,
            colorbarSize: {width: 250, height: 10} as ComponentSize,
            margin: {left: 33, right: 10, top:0, bottom: 20} as Margin,
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
            this.size = { width: target.clientWidth || 0, height: target.clientHeight || 0};
        },
        initChart() {
            const timeFormat = d3.timeFormat('%H:%M');
            let timeBand = temp_table_err_bf[1].check_time - temp_table_err_bf[0].check_time
            let cpuList = ["CPU 0", "CPU 1", "CPU 2", "CPU 3"]
            let ibcList = ["IBC 0", "IBC 1", "IBC 2", "IBC 3"]
            let temp_extent = [0, 16, 22]
            const colorBandTemp = d3.scaleLinear().domain(temp_extent).range(["#8fe5f7", "white", "red"]);
            let vol_extent = [12, 12.5]
            // const colorBandTemp= d3.scaleSequential(["white", "blue"]).domain(vol_extent)
            
            // tooltip event
            let tooltip = d3.select(".tooltip-heat")
            function mouseover(event, item, info, bp, sb) {
                tooltip.transition()
                    .duration(100)
                    .style("opacity", 1);
                
                tooltip.html(`${item} bp${bp} sb${sb} ${info}`)
                    .style("left", `${300}px`)
                    .style("top", `${20}px`)
            }
            function mouseout(event, d) {
                tooltip.transition()
                    .duration(0)
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
                    .ticks(d3.timeMinute.every(30))
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
                    // .padding(0.1) 
                    .paddingInner(0.1);
                
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
                            .attr('width', 0.95 * xScale(table_data[1].check_time) - xScale(table_data[0].check_time))
                            .attr('height', yScale.bandwidth())
                            .attr('fill', d => {
                                if (dataset == 'temp') {
                                    return colorBandTemp(d[`bp${bp}_sb${sb}_cpu_${index}_temp`])
                                }
                                else {
                                    return colorBandVol(d[`bp${bp}_sb${sb}_ibc_${index}_vol`])
                                }
                                    
                            })
                        // .on('mouseover', function (event, d) {
                        //     d3.selectAll('.' + this.getAttribute('class'))
                        //         .transition()
                        //         // .duration(300)
                        //         .attr('opacity', 0.7);
                        //     mouseover(event, `CPU ${index}`, `${d[`bp${bp}_sb${sb}_cpu_${index}_temp`]} °C`,
                        //         bp, sb)
                        // })
                        // .on('mouseout', function (event, d) {
                        //     d3.selectAll('.' + this.getAttribute('class'))
                        //         .transition()
                        //         // .duration(100)
                        //         .attr('opacity', '1');
                        //     mouseout(event, d)
                        // })
                        // .on('click', (event, d) => {
                        //     d3.selectAll('.' + this.getAttribute('class'))
                        //         .transition()
                        //         // .duration(100)
                        //         .attr('opacity', 0.85);
                        // })
                }   
                
            }
            
            // temp
            const colorbar = d3.select("#temp-colorbar")
            let defs = colorbar.append("defs")
            let linearGradient = defs.append("linearGradient")
                .attr("id", "linear-gradient");

            linearGradient.selectAll("stop")
                .data(colorBandTemp.ticks(10).map((t, i, n) => {
                    return ({ offset: `${100*i/n.length}%`, color: colorBandTemp(t) })
                }))    
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
                .domain([colorBandTemp.domain()[0], colorBandTemp.domain()[2]])
                .range([this.margin.left, this.colorbarSize.width - this.margin.right])
            
            const colorAxisTicks = d3.axisBottom(colorAxisScale)
                .ticks(5) 
                .tickSize(-this.colorbarSize.height)
            const colorAxis = colorbar.append("g")
            .attr('transform', `translate(${0}, ${this.colorbarSize.height})`)
            .call(colorAxisTicks)
            
            let parameter = this;
            d3.select("#selectButton").on("change", function(d) {
                let selectedOption = d3.select(this).property("value")
                bp_select = d3.select(this).property("value")
                update(parameter, bp_select, sb_select)
            })
            d3.select("#selectButtonSb").on("change", function(d) {
                let selectedOption = d3.select(this).property("value")
                sb_select = d3.select(this).property("value")
                update(parameter, bp_select, sb_select)
            })
            const chartContainer = d3.select('#heatmap-svg')
                .attr('viewBox', [0, 0, this.svgSizeBf.width, this.svgSizeBf.height])     
            chart_init(chartContainer, this, bp_err, sb_err, temp_table_err_bf, 'temp', true, true, true)

            const chartContainer_af = d3.select('#heatmap-svg-af')
                .attr('viewBox', [0, 0, this.svgSizeAf.width, this.svgSizeAf.height])
            chart_init(chartContainer_af, this, bp_err, sb_err, temp_table_err_af, 'temp', false, false, true)

            function chart_bpsb(bp: number, sb: number) {
                let chartContainerBf = d3.select(`#heatmap-bp${bp}-sb${sb}-bf`)
                .attr('viewBox', [0, 0, parameter.svgSizeBf.width, parameter.svgSizeBf.height])                
                chart_init(chartContainerBf, parameter, bp, sb, temp_table_err_bf, 'temp', true, true, true)

                let chartContainerAf = d3.select(`#heatmap-bp${bp}-sb${sb}-af`)
                .attr('viewBox', [0, 0, parameter.svgSizeAf.width, parameter.svgSizeAf.height])
                chart_init(chartContainerAf, parameter, bp, sb, temp_table_err_af, 'temp', false, false, true)
            }
            const bpList = [0, 1]
            const sbList = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            bpList.forEach((bp) => {
                sbList.forEach((sb) => {
                    if (!(bp==0 && sb ==6)) {
                        chart_bpsb(bp, sb)
                    }
                })
            })
            
            // const chartContainerNorVolSelect_af = d3.select('#heatmap-svg-vol-nor-select-af')
                // .attr('viewBox', [0, 0, this.svgSizeAf.width, this.svgSizeAf.height])
            
            // function update(para, bp, sb) {
            // }
            // let line_tooltip_content = d3.selectAll('.tooltip').text()
            // if (line_tooltip_content.includes('cpu')) {
            //     let part_of_content = line_tooltip_content.split('_')
            //     let bp_point = Number(String(part_of_content[0]).substring(2))
            //     let sb_point = Number(String(part_of_content[1]).substring(2))
            //     if ((bp_point != bp_select) || sb_point != sb_select) {
            //         update(this, bp_point, sb_point)
            //         bp_select = bp_point;
            //         sb_point = sb_point;
            //     }
            //     console.log(bp_select, sb_select)
            // }
                
        }
    },
    watch: {
        size(newSize) {
            if (newSize.width > 0 && newSize.height > 0) {
                d3.select('.svg-container-bf').selectAll('*').remove()
                d3.select('.svg-container-bf').selectAll('*').remove()
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
        <div v-if="dataset == 'temp'" id ="root">
            <div class="row">
                <h5 class="error-label">Error node</h5>
                <svg id="temp-colorbar" class = "colorbar"></svg>
            </div>
            <div class="fixed"> 
                <div class = 'column fixed-left'>
                    <div class="caption-row">
                        <p class="before">Before</p>
                        <p class="after">After</p>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP0 SB0</h3>
                        <svg id="heatmap-bp0-sb0-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp0-sb0-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP0 SB1</h3>
                        <svg id="heatmap-bp0-sb1-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp0-sb1-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP0 SB2</h3>
                        <svg id="heatmap-bp0-sb2-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp0-sb2-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP0 SB3</h3>
                        <svg id="heatmap-bp0-sb3-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp0-sb3-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP0 SB4</h3>
                        <svg id="heatmap-bp0-sb4-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp0-sb4-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP0 SB5</h3>
                        <svg id="heatmap-bp0-sb5-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp0-sb5-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row error-container">
                        <h3 class ='h3-inline'>BP0 SB6</h3>
                        <svg id="heatmap-svg" class = "svg-container-bf"></svg>
                        <svg id="heatmap-svg-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP0 SB7</h3>
                        <svg id="heatmap-bp0-sb7-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp0-sb7-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP0 SB8</h3>
                        <svg id="heatmap-bp0-sb8-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp0-sb8-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP0 SB9</h3>
                        <svg id="heatmap-bp0-sb9-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp0-sb9-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP0 SB10</h3>
                        <svg id="heatmap-bp0-sb10-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp0-sb10-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP0 SB11</h3>
                        <svg id="heatmap-bp0-sb11-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp0-sb11-af" class = "svg-container-af"></svg>
                    </div>
                </div>
                <div class="column fixed-right">
                    <div class="caption-row">
                        <p class="before">Before</p>
                        <p class="after">After</p>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP1 SB0</h3>
                        <svg id="heatmap-bp1-sb0-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp1-sb0-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP1 SB1</h3>
                        <svg id="heatmap-bp1-sb1-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp1-sb1-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP1 SB2</h3>
                        <svg id="heatmap-bp1-sb2-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp1-sb2-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP1 SB3</h3>
                        <svg id="heatmap-bp1-sb3-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp1-sb3-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP1 SB4</h3>
                        <svg id="heatmap-bp1-sb4-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp1-sb4-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP1 SB5</h3>
                        <svg id="heatmap-bp1-sb5-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp1-sb5-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP1 SB6</h3>
                        <svg id="heatmap-bp1-sb6-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp1-sb6-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP1 SB7</h3>
                        <svg id="heatmap-bp1-sb7-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp1-sb7-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP1 SB8</h3>
                        <svg id="heatmap-bp1-sb8-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp1-sb8-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP1 SB9</h3>
                        <svg id="heatmap-bp1-sb9-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp1-sb9-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP1 SB10</h3>
                        <svg id="heatmap-bp1-sb10-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp1-sb10-af" class = "svg-container-af"></svg>
                    </div>
                    <div class="row">
                        <h3 class='h3-inline'>BP1 SB11</h3>
                        <svg id="heatmap-bp1-sb11-bf" class = "svg-container-bf"></svg>
                        <svg id="heatmap-bp1-sb11-af" class = "svg-container-af"></svg>
                    </div>
                </div>
            </div>
        </div>
        <div v-else>
        </div>
        <div class = "tooltip-heat"></div>
    </div>
</template>

<style scoped>
.heatmapContainer {
    width: 100%;
    height: 100%;
    font-family: 'Helvetica Neue', sans-serif;
    text-align: center;
}
.svg-container-bf {
    height: 100px;
    width: 130px; 
}
.svg-container-af {
    height: 100px;
    width: 360px; 
}
.colorbar{
    margin-top: 20px;
    height: 20px;
    width: 250px; 
    margin-right: 20px;
}
.error-container {
    background-color:rgb(251, 216, 184);
    border-radius: 10px;
}
.error-label {
    display: flex;
    flex-direction: center;
    background-color:rgb(251, 216, 184);
    border-radius: 10px;
    padding: 8px;
}
.fixed {
    display: flex;
}
.tooltip-heat{
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
.caption-row {
    display: flex;
    width: 100%;
    font-size: 10px;
    padding: 0;
}
.before { 
    transform: translateX(122px);
}
.after { 
    transform: translateX(300px);
}
.h3-inline {
    font-size: 14px;
    transform-origin: top left;
    transform: translateY(70%) translateX(50%) rotate(-90deg);
    color: gray;
}

.fixed-left {
    padding-left: 10px;
}

.fixed-right {
    flex: 1;
}
.column {
    flex-direction: column;
}
.row {
    padding: 5px;
    display: flex;
    width: 100%; 
}
</style>