
<template>
  <div class="card">
    <Chart
      type="doughnut"
      :data="chartData"
      :options="chartOptions"
      class="h-full h-30rem w-full w-30rem"
    />
  </div>
</template>

<script>

export default {
    props: {
        labels: {
            type: Array,
            required: true,
            default: () => []
        },
        colors: {
            type: Object,
            required: true,
            default: () => ({ rgbColors: [], rgbaColors: [] })
        },
        data: {
            type: Array,
            required: true,
            default: () => []
        }
    },
    watch: {
        colors: {
            handler () {},
            deep: true,
            immediate: true
        },
        labels: {
            handler () {},
            deep: true,
            immediate: true
        },
        data: {
            handler () {
                this.chartData = this.setChartData();
                this.chartOptions = this.setChartOptions();
            },
            deep: true,
            immediate: true
        }
    },
    data () {
        return {
            chartData: null,
            chartOptions: {
                cutout: '60%'
            }
        };
    },
    mounted () {
        this.chartData = this.setChartData();
        this.chartOptions = this.setChartOptions();
    },
    methods: {
        setChartData () {
            return {
                labels: this.labels,
                datasets: [
                    {
                        data: this.data,
                        backgroundColor: this.colors.rgbColors,
                        hoverBackgroundColor: this.colors.rgbaColors
                    }
                ]
            };
        },
        setChartOptions () {
            const documentStyle = getComputedStyle(document.documentElement);
            const textColor = documentStyle.getPropertyValue('--text-color');

            return {
                plugins: {
                    legend: {
                        labels: {
                            cutout: '60%',
                            color: textColor
                        }
                    }
                }
            };
        }
    }
};
</script>
