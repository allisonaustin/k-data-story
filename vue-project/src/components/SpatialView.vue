<script lang="ts">
import * as d3 from 'd3';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';
import { errorNode, normalNode } from '../colors';

const data = await d3.csv('../../data/k_data_processed.csv');
const rack_err = 'l7'
const rack_norm = 'm5'

export default {
    data() {
        return {
            size: { width: 500, height: 500 } as ComponentSize,
            margin: {left: 40, right: 0, top: 20, bottom: 20} as Margin,
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
            const tooltip = d3.select('.tooltip')
            
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
                .attr('fill', d => {
                    if (d.letter + d.num === rack_err) {
                        return errorNode;
                    } else if (d.letter + d.num === rack_norm) {
                        return normalNode;
                    } else {
                        return 'lightgray';
                    }
                })
                .attr('stroke', 'white')
                .attr('fill-opacity', 0.8)

            grid.on('mouseover', function (event, d) {
                    const [xPos, yPos] = d3.pointer(event);

                    if ((d.letter + d.num != rack_err) && (d.letter + d.num != rack_norm)) {
                        d3.select(this)
                            .attr('fill', 'gray')
                    } else {
                        d3.select(this)
                            .attr('fill-opacity', 1)
                    }
                    
                    tooltip.transition()
                        .duration(200)
                        .style('opacity', .9);

                    // node content
                    tooltip.html(`${d.letter + d.num}`)
                        .style('left', `${xPos + 80}px`)
                        .style('top', `${yPos + 300}px`)
                        .style('opacity', 1);
                    
            })
            // hide tooltip
            .on('mouseout', function (event, d) {
                tooltip.transition()
                    .duration(500)
                    .style('opacity', 0);

                // resetting style
                if ((d.letter + d.num != rack_err) && (d.letter + d.num != rack_norm)) {
                        d3.select(this)
                            .attr('fill', 'lightgray')
                    } else {
                        d3.select(this)
                            .attr('fill-opacity', 0.8)
                    }
            });

            grid.filter(d => (d.letter + d.num == rack_err) || (d.letter + d.num == rack_norm))
                .attr('width', d => xScale.bandwidth() * 1.5) 
                .attr('height', d => yScale.bandwidth() * 1.5)
                .attr('x', d => xScale(d.letter) - (xScale.bandwidth() * 0.25)) 
                .attr('y', d => yScale(String(d.num)) - (yScale.bandwidth() * 0.25));
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
        <div class="tooltip"></div>
    </div>
</template>

<style scoped>
.chartContainer {
    height: 500px;
    width: 500px;
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