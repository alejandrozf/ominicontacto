<template>
  <div>
    <div class="grid">
      <div
        v-for="(item, index) in reportData.active_campaigns"
        :key="item"
        class="col-12 md:col-6 lg:col-3"
      >
        <CampaingActiveChart
          :chartName="index"
          :chartData="item"
        ></CampaingActiveChart>
      </div>
    </div>
    <br />
    <div class="grid">
      <StateAgentsChart
        :chartName="state_agents"
        :chartData="reportData.state_agents"
        class="col-12 md:col-6 lg:col-6"
      />
      <ContactedCallsChart
        :chartName="contacted_calls"
        :chartData="reportData.contacted_calls"
        class="col-12 md:col-6 lg:col-3 p-lg-offset-2"
      />
    </div>
  </div>
</template>
<script>
import CampaingActiveChart from '@/components/DashboardSupervisionCharts/CampaingActiveChart.vue';
import StateAgentsChart from '@/components/DashboardSupervisionCharts/StateAgentsChart';
import ContactedCallsChart from '@/components/DashboardSupervisionCharts/ContactedCallsChart';
export default {
    props: {
        reportData: Object
    },
    components: {
        CampaingActiveChart,
        StateAgentsChart,
        ContactedCallsChart
    },
    setup () {}
};
</script>
