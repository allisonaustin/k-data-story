<script lang="ts">
import * as d3 from 'd3';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';
import { errorNode, normalNode } from '../colors';

const data = await d3.csv('../../processed_data/k_data_processed.csv');
const rack_err = 'l7'
const rack_norm = 'm5'

export default {
    data() {
        return {
            size: { width: 500, height: 500 } as ComponentSize,
            margin: {left: 40, right: 100, top: 20, bottom: 20} as Margin,
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
            if (!target) return;
            this.size = { width: target.clientWidth || 0, height: target.clientHeight || 0};
        },
        initChart() {
            let chartContainer = d3.select('#rack-space-svg')
                .attr('viewBox', [0, 0, this.size.width, this.size.height])
            const tooltip = d3.select('.tooltip')
            
            let rack_letters = 'abcdefghijklmnopqrstuvwx'.split('');;
            let rack_nums = d3.range(45, 0, -1);
            let padding = 30;
            const scale = 4;

            let xScale = d3.scaleBand()
                    .domain(rack_letters)
                    .range([padding, this.size.width - this.margin.right])
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
                .attr('width', d => (d.letter == rack_err[0] && d.num == rack_err[1]) ? xScale.bandwidth() * scale : xScale.bandwidth())
                .attr('height', d => (d.letter == rack_err[0] && d.num == rack_err[1]) ? yScale.bandwidth() * scale : yScale.bandwidth())
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
                        .style("cursor", "pointer")
                }
                
                tooltip.transition()
                    .duration(200)
                    .style('opacity', .9);

                // node content
                tooltip.html(`${d.letter + d.num}`)
                    .style('left', `${xPos}px`)
                    .style('top', `${yPos + 100}px`)
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


            // annotating nodes on grid
            const lineStartX = xScale(rack_err[0]) + xScale.bandwidth() / 2;
            const lineStartY = yScale(rack_err[1]) + yScale.bandwidth() / 2;
            const lineEndX = lineStartX + this.size.width / 2.5; 
            const lineEndY = lineStartY; 
            const line1 = chartContainer.append('line')
                .attr('x1', lineStartX)
                .attr('y1', lineStartY)
                .attr('x2', lineStartX)
                .attr('y2', lineStartY)
                .attr('stroke', 'black') 
                .attr('stroke-width', 1)
                .transition()
                .duration(1000)
                .attr('x2', lineEndX)
                .attr('y2', lineEndY)

            const errorNote = chartContainer.append('text')
                .attr('x', lineEndX + 10)
                .attr('y', lineStartY + 3)
                .attr('text-anchor', 'right')
                .style('font-size', '10')
                .style('font-style', 'italic')
                .text('Error rack')

            const _lineStartX = xScale(rack_norm[0]) + xScale.bandwidth() / 2;
            const _lineStartY = yScale(rack_norm[1]) + yScale.bandwidth() / 2;
            const _lineEndX = _lineStartX + this.size.width / 2.7; 
            const _lineEndY = _lineStartY; 

            const line2 = chartContainer.append('line')
                .attr('x1', _lineStartX)
                .attr('y1', _lineStartY)
                .attr('x2', _lineStartX)
                .attr('y2', _lineStartY)
                .attr('stroke', 'black') 
                .attr('stroke-width', 1)
                .transition()
                .duration(1000)
                .attr('x2', _lineEndX)
                .attr('y2', _lineEndY)

            const note = chartContainer.append('text')
                .attr('x', _lineEndX + 10)
                .attr('y', _lineEndY + 3)
                .attr('text-anchor', 'right')
                .style('font-size', '10')
                .style('font-style', 'italic')
                .text('Normal rack')
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