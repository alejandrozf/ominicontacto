<template>
    <div class="card">
        <div class="p-field p-col-12 p-md-4">
            <h5>Active {{chartName}} Campaigns</h5>
            <Knob v-model="basicData" disabled :min="0" :max="1000" alueColor="SlateGray" rangeColor="MediumTurquoise"/>
        </div>
    </div>
</template>
<script>
import { ref, watch } from 'vue'
import Knob from 'primevue/knob';
export default {
    props: { 
        chartData: Number, 
        chartName: String
    },
    components: {
        Knob,
    },
    setup(props) {
        const basicData = ref({
            value: 0,
        });

        watch(props.chartData, (newValue) => {
            updateBasicData(newValue);
        })

        const updateBasicData = (newData) => {
            basicData.value = newData;
        }
        
        updateBasicData(props.chartData);

        return {
            basicData
        }
    },
}
</script>
