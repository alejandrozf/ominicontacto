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
                      <h5 class="text-center">{{ $t("views.dashboard_home_page.authenticated_agents") }}</h5>
                      <StateAgentsChartLine
                          :chartLineInterval="chartLineIntervalAuth"
                          :chartLineEventYesterdayData="chartLineAuthEventYesterdayData"
                          :chartLineEventTodayData="chartLineAuthEventTodayData"
                      >
                      </StateAgentsChartLine>
                  </div>
                  <div class="col-12">
                      <h5 class="text-center">{{ $t("views.dashboard_home_page.califications") }}</h5>
                      <StateAgentsChartLine
                          :chartLineInterval="chartLineIntervalCalification"
                          :chartLineEventYesterdayData="chartLineCalificationEventYesterdayData"
                          :chartLineEventTodayData="chartLineCalificationEventTodayData"
                      >
                      </StateAgentsChartLine>
                  </div>
                  <div class="grid">
                      <StateAgentsChart
                        :chartData="reportData.state_agents"
                        class="col-12 md:col-6 lg:col-6"
                      />
                      <ContactedCallsChart
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
import CampaingActiveChart from '@/components/supervisor/supervision_dashboard/charts/CampaingActiveChart.vue';
import StateAgentsChart from '@/components/supervisor/supervision_dashboard/charts/StateAgentsChart';
import ContactedCallsChart from '@/components/supervisor/supervision_dashboard/charts/ContactedCallsChart';
import StateAgentsChartLine from '@/components/supervisor/supervision_dashboard/charts/StateAgentsChartLine';
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
