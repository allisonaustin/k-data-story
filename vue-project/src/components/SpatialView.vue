<script lang="ts">
import * as d3 from 'd3';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';
import { pallette } from '../colors';

const data = await d3.csv('../../data/k_data_processed.csv');

export default {
    data() {
        return {
            size: { width: 700, height: 600 } as ComponentSize,
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
        onResize: debounce(function () {
            if (this.rackViewContainer) {
                this.size = {
                    width: this.rackViewContainer.clientWidth,
                    height: this.rackViewContainer.clientHeight,
                };
            }
        }, 100),
        initChart() {
            let chartContainer = d3.select('#rack-space-svg')
                .attr('viewBox', [0, 0, this.size.width, this.size.height])
                .attr('style', 'max-width: 100%; height: auto;')
            
            let rack_letters = 'abcdefghijklmnopqrstuvwx'.split('');;
            let rack_nums = d3.range(1, 46);
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

            const xAxis = d3.axisBottom(xScale);
            const yAxis = d3.axisLeft(yScale);

            chartContainer.append('g')
                .attr('transform', `translate(0, ${this.size.height - padding})`)
                .call(xAxis)

            chartContainer.append('g')
                .attr('transform', `translate(${padding}, 0)`)
                .call(yAxis)
        
            chartContainer.append('g')
                .selectAll('rect')
                .data(rack_letters.flatMap(letter => rack_nums.map(num => ({ letter, num: String(num) }))))
                .enter()
                .append('rect')
                .attr('x', d => xScale(d.letter))
                .attr('y', d => yScale(String(d.num)))
                .attr('width', xScale.bandwidth())
                .attr('height', yScale.bandwidth())
                .attr('fill', 'lightgray')
                .attr('stroke', 'white')
                // .on('mouseover', (d, i) => {
                //     chartContainer.append('text')
                //     .attr('id', 'popup')
                //     .attr('x', x(d%cols) - 10)
                //     .attr('y', y(Math.floor(d/cols) - 5))
                //     .text(`${d}`);
                // })
                // .on('mouseout', () => chartContainer.select('#popup').remove());
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
        <svg id="rack-space-svg" width="100%" height="100%">
        </svg>
    </div>
</template>

<style scoped>
.chart-container{
    height: 100%;
}
</style>