/* global VueECharts */

import Vue from '../../JS/ext/vue.js';

Vue.component('v-chart', VueECharts);
var app = new Vue({
    components: {
        'v-chart': VueECharts
    },
    el: '#app1',
    data () {
        let data = [];

        for (let i = 0; i <= 360; i++) {
            let t = i / 180 * Math.PI;
            let r = Math.sin(2 * t) * Math.cos(2 * t);
            data.push([r, i]);
        }

        return {
            polar: {
                title: {
                    text: 'VueECharts example'
                },
                legend: {
                    data: ['line']
                },
                polar: {
                    center: ['50%', '54%']
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross'
                    }
                },
                angleAxis: {
                    type: 'value',
                    startAngle: 0
                },
                radiusAxis: {
                    min: 0
                },
                series: [
                    {
                        coordinateSystem: 'polar',
                        name: 'line',
                        type: 'line',
                        showSymbol: false,
                        data: data
                    }
                ],
                animationDuration: 2000
            }
        };
    }
});
