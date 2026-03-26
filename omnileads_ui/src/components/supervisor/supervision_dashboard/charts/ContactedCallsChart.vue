<template>
  <div class="dashboard-donut-chart">
    <Chart type="doughnut" :data="basicData" :options="chartOptions" :height="120" />
  </div>
</template>
<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';
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
                cutout: '68%',
                plugins: {
                    tooltips: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: textColor.value,
                            usePointStyle: true,
                            boxWidth: 10,
                            boxHeight: 10
                        }
                    }
                }
            };
        });
        const basicData = computed(() => {
            const colors = ['#8FC641', '#FF7B72'];
            return Object.entries(props.chartData).reduce(
                function (prev, [key, val], currIdx) {
                    prev.labels.push(t(`views.dashboard_home_page.call_sumary_${key}`));
                    prev.datasets[0].data.push(val);
                    prev.datasets[0].backgroundColor.push(colors[currIdx % 2]);
                    return prev;
                },
                {
                    labels: [],
                    datasets: [
                        {
                            data: [],
                            backgroundColor: []
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
.dashboard-donut-chart,
.dashboard-donut-chart canvas {
  height: 100%;
}
</style>
