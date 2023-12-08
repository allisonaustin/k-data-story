<script lang="ts">
import * as d3 from "d3";
import { isEmpty, debounce, range } from 'lodash';
import { ComponentSize, Margin, ContainerRect } from '../types';

let datum = []
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
                    { axis: "distance", value: +d.distance}, // distance from error rack
                    { axis: "pol_a_temp", value: +d.pol_a_temp_max },
                    { axis: "pol_b_temp", value: +d.pol_b_temp_max },
                    { axis: "pol_a_vol", value: +d.pol_a_vol_max },
                    { axis: "pol_b_vol", value: +d.pol_b_vol_max },
                    { axis: "pol_c_vol", value: +d.pol_c_vol_max },
                    { axis: "a_rpm", value: +d.a_rpm_max },
                    { axis: "b_rpm", value: +d.b_rpm_max },
                    { axis: "water_temp", value: +d.water_temp },
                ],
            }
            datum.push(Obj)
        })
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
            
            const keys = datum[0].values.map(d => d.axis);
            let theta = -Math.PI/2
            let angleList = [] as number[]
            for (let i = 0; i < numAxes; i++) {
                angleList.push(theta)
                theta += angleSlice
            }
            // background circle
            let r = [0, radius / 4, 2 * radius / 4, 3 * radius / 4, radius]
            const backCircle = group.selectAll(".backgroundCircle")
                .data(r)
                .enter()
                .append('circle')
                    .attr("cx", origin[0])
                    .attr("cy", origin[1])
                    .attr("r", (d) => d)
                .attr("stroke", "grey")
                .attr('fill', 'none')
                .attr('stroke-width', 0.5)
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
                extentList.push([0, d3.extent(datum.map(k => k.values[i].value))[1]])
            }) 
            let rScale = []
            extentList.forEach((d, i) => {
                rScale.push(
                    d3.scaleLinear()
                    .range([0, radius])
                    .domain(d)
                )  
            })
            // color function 
            function colorcode(i) {
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
            let lineRadial = d3.lineRadial()
                .curve(d3.curveCardinalClosed.tension(0.5)) // the higher the tension, the more straigt the line is
                .radius((d, i) => {
                    let scale = rScale[i]
                    return scale(d.value)
                })
                .angle((d, i) => angleList[i])
            let center = group.append('g').attr("transform", `translate(${origin[0]}, ${origin[1]})`)
            
            let radarWrapper = center.selectAll(".radar-wrapper")
                .data(datum).enter()
                .append('g')
            
            let path = radarWrapper.append("path")
                .attr("d", (d) => lineRadial(d.values))
                .attr("stroke", (d, i) => d3.schemeCategory10[i])
                .attr('stroke-width', 0.5)
                .attr('fill', 'none')
            
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
