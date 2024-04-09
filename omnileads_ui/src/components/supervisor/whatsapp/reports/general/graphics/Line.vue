
<template>
  <div class="card">
    <Chart
      type="line"
      :data="chartData"
      :options="chartOptions"
      class="h-30rem"
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
            const label = this.$t('views.whatsapp.reports.general.general_report');
            return {
                labels: this.labels,
                datasets: [
                    {
                        label,
                        data: this.data,
                        fill: false,
                        borderColor: this.colors.rgbColors[0],
                        tension: 0.5
                    }
                ]
            };
        },
        setChartOptions () {
            const documentStyle = getComputedStyle(document.documentElement);
            const textColor = documentStyle.getPropertyValue('--text-color');
            const textColorSecondary = documentStyle.getPropertyValue(
                '--text-color-secondary'
            );
            const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

            return {
                maintainAspectRatio: false,
                aspectRatio: 0.6,
                plugins: {
                    legend: {
                        labels: {
                            color: textColor
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: textColorSecondary
                        },
                        grid: {
                            color: surfaceBorder
                        }
                    },
                    y: {
                        ticks: {
                            color: textColorSecondary
                        },
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
