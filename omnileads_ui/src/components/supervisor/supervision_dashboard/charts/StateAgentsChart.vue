<template>
  <Card>
    <template #title>
      <h5 class="text-center">
        {{ $t("views.dashboard_home_page.agent_status") }}
      </h5>
    </template>
    <template #content>
      <Chart type="bar" :data="basicData" :options="chartOptions"  :height="150"/>
    </template>
  </Card>
</template>
<script>
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

export default {
    props: {
        chartData: Object
    },
    setup (props) {
        const { t } = useI18n();
        const chartOptions = ref({
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
                y: {
                    ticks: {
                        stepSize: 1
                    }
                }
            }
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
