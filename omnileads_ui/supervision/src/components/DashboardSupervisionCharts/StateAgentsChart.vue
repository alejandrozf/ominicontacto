<template>
  <Card>
    <template #title>
      <h5 class="text-center">
        {{ $t("views.dashboard_home_page.agent_status") }}
      </h5>
    </template>
    <template #content>
      <Chart type="bar" :data="basicData" :options="chartOptions"  :height="50"/>
    </template>
  </Card>
</template>
<script>
import { ref, watch } from 'vue';

export default {
    props: {
        chartData: Object,
        chartName: String
    },
    setup (props) {
        const chartOptions = ref({
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

        const basicData = ref({
            labels: ['Ready', 'Oncall', 'Pause'],
            datasets: [
                {
                    data: [],
                    backgroundColor: ['#42A5F5', '#66BB6A', '#FFA726']
                }
            ]
        });

        watch(props.chartData, (newValue) => {
            updateBasicData(newValue);
        });

        const updateBasicData = (newData) => {
            const labels = [];
            const dataSets = [];

            for (const key in newData) {
                labels.push(key);
                dataSets.push(newData[key]);
            }
            basicData.value.labels = labels;
            basicData.value.datasets[0].data = dataSets;
            basicData.value.datasets[0].label = labels[0];
        };

        updateBasicData(props.chartData);

        return {
            chartOptions,
            basicData
        };
    }
};
</script>
