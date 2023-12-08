<script lang="ts">
import * as d3 from "d3";
import { isEmpty, debounce, range } from 'lodash';
import { ComponentSize, Margin, ContainerRect } from '../types';

let datum = []
const rack_list = [ 'k06', 'k07', 'l06', 'l07', 'm05', 'm06', 'm07']
let datasets = [
    '../../data/rack-data-14:30:01.csv',
    '../../data/rack-data-14:55:01.csv',
    '../../data/rack-data-15:00:01.csv'
]

export default {
    props: {
        dataset: {
            type: String,
            required: true,
        }
    },
    data() {
        return {
            size: { width: 0, height: 0 } as ComponentSize,
            legend_size: { width: 400, height: 50 } as ComponentSize,
            margin: {left: 10, right: 10, top: 20, bottom: 60} as Margin,
        }
    }, 
    computed: {
        rerender() {
            return (!isEmpty(this.dataset)) && this.size
        },
        svgId() {
            return `radar-svg-${this.dataset}`;
        }
    },
    async created() {
        if (isEmpty(this.dataset)) return;
        let csvData = await d3.csv(datasets[+this.dataset]);

        
        // modify the data here
        datum = []
        csvData.forEach(d => {
            let Obj = {
                rack: d.rack,
                check_time: d3.timeParse('%Y-%m-%d %H:%M:%S')(d.check_time),
                values: [
                    { axis: "distance", value: +d.distance, value_min: +d.distance}, // distance from error rack
                    { axis: "pol_a_temp", value: +d.pol_a_temp_max, value_min: +d.pol_a_temp_min },
                    { axis: "pol_b_temp", value: +d.pol_b_temp_max, value_min: +d.pol_b_temp_min },
                    { axis: "pol_a_vol", value: +d.pol_a_vol_max, value_min: +d.pol_a_vol_min },
                    { axis: "pol_b_vol", value: +d.pol_b_vol_max, value_min: +d.pol_b_vol_min },
                    { axis: "pol_c_vol", value: +d.pol_c_vol_max, value_min: +d.pol_c_vol_min },
                    { axis: "a_rpm", value: +d.a_rpm_max, value_min: +d.a_rpm_min },
                    { axis: "b_rpm", value: +d.b_rpm_max, value_min: +d.b_rpm_min },
                    { axis: "water_temp", value: +d.water_temp, value_min: +d.water_temp },
                ],
            }
            datum.push(Obj)
        })
        
        function compare(a, b) {
            if (a.rack < b.rack) {
                return 1
            }
            if (a.rack > b.rack) {
                return -1
            } 
            return 0
        }
        datum.sort(compare)
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
            if (datum.length == 0) return;
            let chartContainer = d3.select('#radar-svg-' + this.dataset)
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
                .on('mouseover', (event, d) => {
                    d3.selectAll(".scale-label"+this.dataset).transition().style('opacity', 1)
                })
                .on('mouseout', (event, d) => {
                    d3.selectAll(".scale-label"+this.dataset).transition().style('opacity', 0)
                })
            const keys = datum[0].values.map(d => d.axis);
            let theta = -Math.PI/2
            let angleList = [] as number[]
            for (let i = 0; i < numAxes; i++) {
                angleList.push(theta)
                theta += angleSlice
            }
            // background circle
            let radiusList = [0, radius / 3, 2 * radius / 3, radius]
            const backCircle = group.selectAll(".backgroundCircle")
                .data(radiusList)
                .enter()
                .append('circle')
                    .attr("cx", origin[0])
                    .attr("cy", origin[1])
                    .attr("r", (d) => d)
                .attr("stroke", "grey")
                .attr('fill', 'none')
                .attr('stroke-width', 0.5)
                // .on('mouseover')
            let extentList = [] as number[][]

            // plot axes
            const axes = group.selectAll('.axis')
                .data(keys)
                .enter()
                .append('g')
                .attr('class', 'axis')
            
            // axis line
            axes.append('line')
                .attr('x1', origin[0])
                .attr('y1', origin[1])
                .attr('x2', (d, i) => origin[0] + radius * Math.cos(angleList[i] - Math.PI/2))
                .attr('y2', (d, i) => origin[1] + radius * Math.sin(angleList[i] - Math.PI/2))
                .attr('stroke', 'grey')
                .attr('fill', 'none')
                .attr('stroke-width', 0.5)
            // label for each category
            axes.append('text')
                .attr('x', (d, i) => origin[0] + radius * Math.cos(angleList[i] - Math.PI/2))
                .attr('y', (d, i) => origin[1] + radius * Math.sin(angleList[i] - Math.PI/2))
                .text(d => d)
                .style('text-anchor', (d, i) => {
                    return (Math.cos(angleList[i] - Math.PI/2) < 0)? "end":"begin";
                })
                .attr('class', 'axis-label');
            
            keys.forEach((d, i) => {
                extentList.push([d3.min(datum.map(k => k.values[i].value_min)), d3.max(datum.map(k => k.values[i].value))])
            }) 
            let rScale = []
            extentList.forEach((d, i) => {
                rScale.push(
                    d3.scaleLinear()
                    .range([0, radius])
                    .domain(d)
                )  
            })
            for (let index = 1; index < radiusList.length - 1; index++) {
                axes.append('text')
                // .attr("dy", ".1em")  
                .attr('class', 'scale-label'+this.dataset)
                .attr('x', (d, i) => origin[0] + radiusList[index] * Math.cos(angleList[i] - Math.PI/2))
                .attr('y', (d, i) => origin[1] + radiusList[index] * Math.sin(angleList[i] - Math.PI/2))
                .text((d, i) => Math.round((extentList[i][0]+(extentList[i][1]-extentList[i][0]) * index / radiusList.length) * 100) / 100)
                .style('opacity', 0)
                
            }
            // color function 
            function colorcode(rack: string) {
                let i = rack_list.findIndex(d => d == rack)
                return d3.schemeCategory10[i]
            }

            const chartTitle = chartContainer.append('text')
                .attr('x', this.size.width / 2 + this.margin.left)
                .attr('y', this.size.height - this.margin.top + 10)
                .attr('text-anchor', 'middle')
                .style('fill', 'gray')
                .style('font-style', 'bold')
                .style('font-size', '18')
                .style('font-family', 'Helvetica Neue, sans-serif')
                .text(datasets[+this.dataset].substring(datasets[+this.dataset].length-12, datasets[+this.dataset].length-4))

            // radar chart curve version
            let lineRadial = d3.areaRadial()
                .curve(d3.curveCardinalClosed.tension(0.5)) // the higher the tension, the more straigt the line is
                .outerRadius((d, i) => {
                    let scale = rScale[i]
                    return scale(d.value)
                })
                .innerRadius((d, i) => {
                    let scale = rScale[i]
                    return scale(d.value_min)
                })
                .angle((d, i) => angleList[i])
            let center = group.append('g').attr("transform", `translate(${origin[0]}, ${origin[1]})`)
            
            let radarWrapper = center.selectAll(".radar-wrapper")
                .data(datum).enter()
                .append('g')
            
            let background = radarWrapper.append("path")
                .attr('class', d => d.rack)
                .attr('class', `dataset-${this.dataset}`)
                // .attr('class', "background")
                .attr("d", (d) => lineRadial(d.values))
                .attr("stroke", (d, i) => colorcode(d.rack))
                .attr('stroke-width', 0.5)
                .attr('fill', (d, i) => colorcode(d.rack))
                .style('opacity', 0.2)

            let path = radarWrapper.append("path")
                .attr('class', d => 'tp'+d.rack)
                .attr('class', d => 'front')
                .attr("d", (d) => lineRadial(d.values))
                .attr("stroke", (d, i) => colorcode(d.rack))
                .attr('stroke-width', 1)
                .attr('fill', 'none')
                .style('opacity', 1)

            const legendContainer = d3.select('#legend-svg')
                .attr('width', this.legend_size.width)
                .attr('height', this.legend_size.height)                
                .attr('viewBox', [0, 0, this.legend_size.width, this.legend_size.height])
            if (this.dataset == '1') {
                let legend_group = legendContainer.append('g').attr('transform', `translate(${this.margin.left},${this.margin.top})`)
                .selectAll('.mylegend')
                .data(rack_list).enter()
                .append('g')
                const legend_label = legend_group.append('text')
                    .attr('x', (d, i) => 20 + i * 50)
                    .attr('y', 0)
                    .attr('alignment-baseline', 'middle')
                    .text(d => d)
                    .on('click', (event, d) => {
                        let currentOpacity = d3.select('.'+d).style('opacity')
                        d3.selectAll('.'+d).style('opacity', currentOpacity > 0? 0:0.2)
                        d3.selectAll('.tp'+d).style('opacity', currentOpacity > 0? 0:1);
                    })
                    // .on('mouseover', (event, d) => {
                    //     let path_class = d3.selectAll('.'+d)
                    //     console.log(path_class)
                    //     d3.selectAll('path')
                    //     .filter(otherPath => otherPath !== path_class[0])
                    //     .style('opacity', 0)
                        // d3.selectAll('.'+d).style('opacity', 0.2)
                        // d3.selectAll('.tp'+d).style('opacity', 1);
                    // })
                    // .on('mouseout', (event, d) => {
                    //     d3.selectAll('.background').style('opacity', 0.2)
                    //     d3.selectAll('.front').style('opacity', 1);
                    // })
                legend_group.append('circle')
                    .attr('r', 5)
                    .attr('cx', (d, i) => 10 + i * 50)
                    .attr('cy', 0)
                    .attr('fill', (d, i) => colorcode(d))
                    .style('opacity', 0.5)
                    .on('click', (event, d) => {
                        let currentOpacity = d3.select('.'+d).style('opacity')
                        d3.selectAll('.'+d).style('opacity', currentOpacity > 0? 0:0.2);
                        d3.selectAll('.tp'+d).style('opacity', currentOpacity > 0? 0:1);
                    }) 
            }
            
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
    <div v-if="dataset == '1'">
        <svg id="legend-svg"></svg>
    </div>
    
    <div ref="radarChartContainer" class="radar-container">
        <svg :id="svgId"></svg>
        <div class="tooltip"></div>
    </div>
</template>

<style scoped>
.radar-container {
    height: 400px;
    width: 500px;
    font-family: 'Helvetica Neue', sans-serif;
    text-align: center;
    font-size: 14px;
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
