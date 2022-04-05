<template>
    <Card>
        <template #title>
            <h5 class='p-text-center'>
                {{$t('pages.dashboard_home_page.active_campaign_by_type', {type: titleize(chartName)})}}
            </h5>
        </template>
        <template #content>
            <div class="p-d-flex p-jc-center">
                <Knob v-model="basicData" readonly :min="0" :max="500" :size="150" alueColor="#fffff" rangeColor="#8FC641"/>
            </div>
        </template>
    </Card>
</template>
<script>
import { ref, watch } from 'vue';

export default {
    props: {
        chartData: Number,
        chartName: String
    },
    methods: {
        titleize (txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        }
    },
    setup (props) {
        const basicData = ref({
            value: 0
        });

        watch(props.chartData, (newValue) => {
            updateBasicData(newValue);
        });

        const updateBasicData = (newData) => {
            basicData.value = newData;
        };

        updateBasicData(props.chartData);

        return {
            basicData
        };
    }
};
</script>
