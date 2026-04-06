<template>
    <div class="dashboard-line-chart">
        <Chart type="line" :data="basicData" :options="basicOptions" />
    </div>
 </template>

<script>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';

export default {
    props: {
        chartNameHoy: String,
        chartNameAyer: String,
        chartLineInterval: Object,
        chartLineEventYesterdayData: Object,
        chartLineEventTodayData: Object
    },
    setup (props) {
        const { t } = useI18n();
        const isDark = ref(false);

        let observer = null;
        onMounted(() => {
            isDark.value = document.documentElement.classList.contains('dark-mode');
            observer = new MutationObserver(() => {
                isDark.value = document.documentElement.classList.contains('dark-mode');
            });
            observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
        });

        onUnmounted(() => {
            if (observer) observer.disconnect();
        });

        const textColor = computed(() => isDark.value ? '#f2f3f5' : '#495057');
        const gridColor = computed(() => isDark.value ? 'rgba(255,255,255,0.05)' : '#ebedef');

        const basicData = computed(() => {
            return {
                labels: props.chartLineInterval,
                datasets: [
                    {
                        label: t('views.dashboard_home_page.today'),
                        data: props.chartLineEventTodayData,
                        fill: true,
                        tension: 0.35,
                        borderWidth: 3,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        pointHoverBorderWidth: 2,
                        borderColor: '#5DA3FF',
                        backgroundColor: 'rgba(93, 163, 255, 0.16)'
                    },
                    {
                        label: t('views.dashboard_home_page.yesterday'),
                        data: props.chartLineEventYesterdayData,
                        fill: false,
                        tension: 0.35,
                        borderDash: [6, 6],
                        borderWidth: 2,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        borderColor: '#FFB54D'
                    }
                ]
            };
        });

        const basicOptions = computed(() => {
            return {
                maintainAspectRatio: false,
                animation: {
                    duration: 0
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: textColor.value,
                            usePointStyle: true,
                            boxWidth: 10,
                            boxHeight: 10
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: textColor.value,
                            maxTicksLimit: 12
                        },
                        grid: {
                            color: gridColor.value,
                            drawTicks: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: textColor.value,
                            stepSize: 1
                        },
                        grid: {
                            color: gridColor.value,
                            drawTicks: false
                        }
                    }
                }
            };
        });

        return { basicData, basicOptions };
    }
};
</script>
<style>
.dashboard-line-chart,
.dashboard-line-chart .p-chart,
.dashboard-line-chart canvas {
  height: 100% !important;
}

.dashboard-line-chart .p-chart {
  width: 100%;
}
</style>
