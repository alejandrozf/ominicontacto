<template>
 <div>
    <Splitter style="height: 300px" layout="vertical">
        <SplitterPanel>
        <div class="row"> 
            <div class="col-md-2" v-for="(item, index) in reportData.active_campaigns"  :key="item">
                <CampaingActiveChart :chartName="index" :chartData="item"></CampaingActiveChart>
            </div>
        </div>
        </SplitterPanel>
        <SplitterPanel>
        <div class="row"> 
            <div class="col-md-4">
                <StateAgentsChart :chartName="state_agents" :chartData="reportData.state_agents"></StateAgentsChart>
            </div>
            <div class="col-md-2">
                <ContactedCallsChart :chartName="contacted_calls" :chartData="reportData.contacted_calls"></ContactedCallsChart>
            </div>
        </div>
        </SplitterPanel>
    </Splitter>
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
