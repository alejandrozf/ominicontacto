<template>
    <div>
        <Chart type="line" :data="basicData" :options="basicOptions" :height="50" />
    </div>
 </template>

<script>
import { computed, ref } from 'vue';

export default {
    props: {
        chartNameHoy: String,
        chartNameAyer: String,
        chartLineInterval: Object,
        chartLineEventYesterdayData: Object,
        chartLineEventTodayData: Object
    },
    setup (props) {
        const basicData = computed(() => {
            return {
                labels: props.chartLineInterval,
                datasets: [
                    {
                        label: 'Hoy',
                        data: props.chartLineEventTodayData,
                        fill: false,
                        borderColor: '#42A5F5'
                    },
                    {
                        label: 'Ayer',
                        data: props.chartLineEventYesterdayData,
                        fill: false,
                        borderColor: '#FFA726'
                    }
                ]
            };
        });

        const basicOptions = ref(
            {
                animation: {
                    duration: 0
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#495057'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#495057'
                        },
                        grid: {
                            color: '#ebedef'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#495057',
                            stepSize: 1
                        },
                        grid: {
                            color: '#ebedef'
                        }
                    }
                }
            }
        );

        return { basicData, basicOptions };
    }
};
</script>
