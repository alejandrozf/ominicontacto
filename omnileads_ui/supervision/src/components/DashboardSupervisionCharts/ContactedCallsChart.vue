<template>
    <Card>
        <template #title>
            <h5 class='p-text-center'>{{$t('pages.dashboard_home_page.call_sumary')}}</h5>
        </template>
        <template #content>
            <Chart type="pie" :data="basicData" :options="chartOptions" />
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
        const chartOptions = ref(
            {
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
            }
        );
        const basicData = ref({
            labels: [''],
            datasets: [
                {
                    data: [],
                    backgroundColor: [
                        '#8FC641',
                        '#196F3D'
                    ]
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
        };
        updateBasicData(props.chartData);

        return {
            chartOptions,
            basicData
        };
    }
};
</script>
