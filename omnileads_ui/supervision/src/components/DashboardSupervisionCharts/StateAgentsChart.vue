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

export default {
    props: {
        chartData: Object,
        chartName: String
    },
    setup (props) {
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
                    prev.labels.push(key);
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
                            label: 'Ready'
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
