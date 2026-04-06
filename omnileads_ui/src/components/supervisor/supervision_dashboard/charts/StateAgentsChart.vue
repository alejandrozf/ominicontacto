<template>
  <div class="dashboard-bar-chart">
    <Chart type="bar" :data="basicData" :options="chartOptions" :height="120" />
  </div>
</template>
<script>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';

export default {
    props: {
        chartData: Object
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

        const chartOptions = computed(() => {
            return {
                maintainAspectRatio: false,
                animation: {
                    duration: 0
                },
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            color: textColor.value
                        },
                        grid: {
                            color: isDark.value ? 'rgba(255,255,255,0.06)' : 'rgba(15,23,42,0.08)',
                            drawTicks: false
                        }
                    },
                    x: {
                        ticks: {
                            color: textColor.value
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            };
        });
        const basicData = computed(() => {
            const colors = ['#42A5F5', '#66BB6A', '#FFA726'];
            return Object.entries(props.chartData).reduce(
                function (prev, [key, val], currIdx) {
                    prev.labels.push(t(`views.dashboard_home_page.agent_status_${key}`));
                    prev.datasets[0].data.push(val);
                    prev.datasets[0].backgroundColor.push(colors[currIdx % 3]);
                    return prev;
                },
                {
                    labels: [],
                    datasets: [
                        {
                            data: [],
                            backgroundColor: [],
                            borderRadius: 12,
                            borderSkipped: false,
                            label: t('views.dashboard_home_page.agent_status_ready')
                        }
                    ]
                }
            );
        });
        return {
            chartOptions,
            basicData
        };
    }
};
</script>
<style>
.dashboard-bar-chart,
.dashboard-bar-chart canvas {
  height: 100%;
}
</style>
