<template>
  <Card>
    <template #title>
      <h5 class="text-center">
        {{ $t("views.dashboard_home_page.call_sumary") }}
      </h5>
    </template>
    <template #content>
      <Chart type="pie" :data="basicData" :options="chartOptions"  :height="50" />
    </template>
  </Card>
</template>
<script>
import { ref, computed } from 'vue';
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
                tooltips: {
                    mode: 'index',
                    intersect: false
                },
                legend: {
                    labels: {
                        color: '#495057'
                    }
                }
            }
        });
        const basicData = computed(() => {
            const colors = ['#8FC641', '#196F3D'];
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
