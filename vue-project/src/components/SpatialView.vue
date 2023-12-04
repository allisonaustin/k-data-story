<script lang="ts">
import * as d3 from 'd3';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';

const data = await d3.csv('../../data/k_data_processed.csv');
const rack_err = 'l7'
const rack_norm = 'm5'

export default {
    data() {
        return {
            size: { width: 500, height: 500 } as ComponentSize,
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
            let target = this.$refs.rackViewContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight};
        },
        initChart() {
            let chartContainer = d3.select('#rack-space-svg')
                .attr('viewBox', [0, 0, this.size.width, this.size.height])
            
            let rack_letters = 'abcdefghijklmnopqrstuvwx'.split('');;
            let rack_nums = d3.range(45, 0, -1);
            let padding = 30;

            let xScale = d3.scaleBand()
                    .domain(rack_letters)
                    .range([padding, this.size.width - padding])
                    .padding(0.1)
                    .paddingInner(0.2);

            let yScale = d3.scaleBand()
                .domain(rack_nums.map(String))
                .range([padding, this.size.height - padding])
                .padding(0.1)
                .paddingInner(0.2);

            const xAxis = chartContainer.append('g')
                .attr('transform', `translate(0, ${this.size.height - padding})`)
                .call(d3.axisBottom(xScale))

            const yAxis = chartContainer.append('g')
                .attr('transform', `translate(${padding}, 0)`)
                .call(d3.axisLeft(yScale))

            // rack grid
            const grid = chartContainer.append('g')
                .selectAll('rect')
                .data(rack_letters.flatMap(letter => rack_nums.map(num => ({ letter, num: String(num) }))))
                .enter()
                .append('rect')
                .attr('x', d => xScale(d.letter))
                .attr('y', d => yScale(String(d.num)))
                .attr('width', xScale.bandwidth())
                .attr('height', yScale.bandwidth())
                .attr('fill', d => (d.letter + d.num == rack_err ? '#fb8072' : 'lightgray'))
                .attr('stroke', 'white')

            // const lineStartX = xScale(rack_err[0]) + xScale.bandwidth() / 2;
            // const lineStartY = yScale(rack_err[1]) + yScale.bandwidth() / 2;

            // const lineEndX = lineStartX + this.size.width / 2; 
            // const lineEndY = lineStartY; 

            // const line = chartContainer.append('line')
            //     .attr('x1', lineStartX)
            //     .attr('y1', lineStartY)
            //     .attr('x2', lineStartX)
            //     .attr('y2', lineStartY)
            //     .attr('stroke', 'black') 
            //     .attr('stroke-width', 1)
            //     .transition()
            //     .duration(1000)
            //     .attr('x2', lineEndX)
            //     .attr('y2', lineEndY)
        }
            
    },
    watch: {
        size(newSize) {
            if (newSize.width > 0 && newSize.height > 0) {
                d3.select('#rack-space-svg').selectAll('*').remove()
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
    <div ref="rackViewContainer" class="chartContainer">
        <svg id="rack-space-svg">
        </svg>
    </div>
</template>

<style scoped>
.chartContainer {
    height: 500px;
    width: 500px;
}
</style>