<template>
 <div>
    <div class="p-grid">
        <div v-for="(item, index) in reportData.active_campaigns" :key="item" class="p-col-12 p-md-6 p-lg-3">
            <CampaingActiveChart :chartName="index" :chartData="item"></CampaingActiveChart>
        </div >
    </div>
    <br>
    <div class="p-grid">
        <StateAgentsChart :chartName="state_agents" :chartData="reportData.state_agents" class="p-col-12 p-md-6 p-lg-6" />
        <ContactedCallsChart :chartName="contacted_calls" :chartData="reportData.contacted_calls" class="p-col-12 p-md-6 p-lg-3 p-lg-offset-2" />
    </div>
</div>
</template>
<script>
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';
import CampaingActiveChart from '@/components/DashboardSupervisionCharts/CampaingActiveChart'
import StateAgentsChart from '@/components/DashboardSupervisionCharts/StateAgentsChart'
import ContactedCallsChart from '@/components/DashboardSupervisionCharts/ContactedCallsChart'
export default {
    props:{
        reportData: Object
    },
    components: {
        Splitter,
        SplitterPanel,
        CampaingActiveChart,
        StateAgentsChart,
        ContactedCallsChart
    },
    setup() {
        
    },
}
</script>
