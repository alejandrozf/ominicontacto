<template>
    <div class="card">
            <div  class="p-grid" >
                <div class="p-col-9"> 
                </div>
        </div>
            <h5>Agent Status</h5>
        <Chart type="bar" :data="basicData" :options="chartOptions" />
    </div>
</template>
<script>
import { ref, watch } from 'vue'
import Chart from 'primevue/chart'
export default {
    props: { 
        chartData: Object, 
        chartName: String
    },
    components: {
        Chart,
    },
    setup(props) {
        const chartOptions = ref(
            {
                plugins: {
                    legend: {
                        labels: {
                            color: '#495057'
                        }
                    }
                },
            }
        );

        const basicData = ref({
            labels: [''],
            datasets: [
                {    
                    label: '',
                    backgroundColor: [
                        "#5AF9A3",
                        "#3D786A",
                        "#5AF9F4"
                    ],
                    data: []
                },
            ]
        });

        watch(props.chartData, (newValue) => {
            updateBasicData(newValue);
        })

        const updateBasicData = (newData) => {
            let labels = []
            let dataSets = []
            
            for (let key in newData) {
                labels.push(key)
                dataSets.push(newData[key])
            }
            basicData.value.labels = labels;
            basicData.value.datasets[0].data = dataSets;
            basicData.value.datasets[0].label = labels[0];
        }

        updateBasicData(props.chartData);

        return {
            chartOptions,
            basicData
        }
    },
}
</script>
