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
      <Card style="width: 100rem; margin-bottom: 2em">
          <template #title >
          </template>
          <template #content>
              <div>
                  <div class="col-12">
                      <h5 class="text-center">Agentes</h5>
                      <StateAgentsChartLine
                          :chartLineInterval="chartLineIntervalAuth"
                          :chartLineEventYesterdayData="chartLineAuthEventYesterdayData"
                          :chartLineEventTodayData="chartLineAuthEventTodayData"
                      >
                      </StateAgentsChartLine>
                  </div>
                  <div class="col-12">
                      <h5 class="text-center">Gestiones</h5>
                      <StateAgentsChartLine
                          :chartLineInterval="chartLineIntervalCalification"
                          :chartLineEventYesterdayData="chartLineCalificationEventYesterdayData"
                          :chartLineEventTodayData="chartLineCalificationEventTodayData"
                      >
                      </StateAgentsChartLine>
                  </div>
                  <div class="grid">
                      <StateAgentsChart
                        :chartName="state_agents"
                        :chartData="reportData.state_agents"
                        class="col-12 md:col-6 lg:col-6"
                      />
                      <ContactedCallsChart
                        :chartName="contacted_calls"
                        :chartData="reportData.contacted_calls"
                        class="col-12 md:col-6 lg:col-6"
                      />
                  </div>
              </div>
          </template>
      </Card>
    </div>
  </div>
</template>
<script>
import CampaingActiveChart from '@/components/DashboardSupervisionCharts/CampaingActiveChart.vue';
import StateAgentsChart from '@/components/DashboardSupervisionCharts/StateAgentsChart';
import ContactedCallsChart from '@/components/DashboardSupervisionCharts/ContactedCallsChart';
import StateAgentsChartLine from '@/components/DashboardSupervisionCharts/StateAgentsChartLine';
export default {
    props: {
        reportData: Object,
        chartLineIntervalAuth: Object,
        chartLineIntervalCalification: Object,
        chartLineAuthEventYesterdayData: Object,
        chartLineAuthEventTodayData: Object,
        chartLineCalificationEventYesterdayData: Object,
        chartLineCalificationEventTodayData: Object
    },
    components: {
        CampaingActiveChart,
        StateAgentsChart,
        ContactedCallsChart,
        StateAgentsChartLine
        
    },
    setup () {}
};
</script>
