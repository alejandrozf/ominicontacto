
<template>
  <div class="card">
    <Chart
      type="polarArea"
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
            chartOptions: null
        };
    },
    mounted () {
        this.chartData = this.setChartData();
        this.chartOptions = this.setChartOptions();
    },
    methods: {
        setChartData () {
            return {
                datasets: [
                    {
                        data: this.data,
                        backgroundColor: this.colors.rgbColors,
                        hoverBackgroundColor: this.colors.rgbaColors,
                        label: 'My dataset'
                    }
                ],
                labels: this.labels
            };
        },
        setChartOptions () {
            const documentStyle = getComputedStyle(document.documentElement);
            const textColor = documentStyle.getPropertyValue('--text-color');
            const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

            return {
                plugins: {
                    legend: {
                        labels: {
                            color: textColor
                        }
                    }
                },
                scales: {
                    r: {
                        grid: {
                            color: surfaceBorder
                        }
                    }
                }
            };
        }
    }
};
</script>
