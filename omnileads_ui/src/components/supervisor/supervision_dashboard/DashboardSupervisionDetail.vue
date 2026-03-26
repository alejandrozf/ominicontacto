<template>
  <div class="dashboard-shell">
    <div class="dashboard-status-strip">
      <div class="dashboard-status-cluster">
        <div
          v-for="metric in overviewMetrics"
          :key="metric.label"
          class="dashboard-status-item"
        >
          <span
            class="dashboard-status-dot"
            :style="{ background: metric.color }"
          ></span>
          <span class="dashboard-status-label">{{ metric.label }}</span>
          <strong class="dashboard-status-value">{{ metric.value }}</strong>
        </div>
      </div>

      <div class="dashboard-status-cluster dashboard-status-cluster--right">
        <div
          v-for="metric in resourceMetrics"
          :key="metric.label"
          class="dashboard-status-item"
        >
          <span
            class="dashboard-status-dot"
            :style="{ background: metric.color }"
          ></span>
          <span class="dashboard-status-label">{{ metric.label }}</span>
          <strong class="dashboard-status-value">{{ metric.value }}</strong>
        </div>
      </div>
    </div>

    <div class="grid dashboard-grid">
      <div
        v-for="(item, index) in reportData.active_campaigns"
        :key="index"
        class="col-12 md:col-6 xl:col-3"
      >
        <CampaingActiveChart
          :chartName="index"
          :chartData="item"
        />
      </div>
    </div>

    <div class="grid dashboard-grid">
      <div class="col-12 xl:col-8">
        <section class="dashboard-panel dashboard-panel-hero">
          <header class="dashboard-panel-header">
            <div>
              <span class="dashboard-panel-kicker">
                {{ $t("views.dashboard_home_page.today") }} / {{ $t("views.dashboard_home_page.yesterday") }}
              </span>
              <h3 class="dashboard-panel-title">
                {{ $t("views.dashboard_home_page.authenticated_agents") }}
              </h3>
            </div>
            <div class="dashboard-panel-emphasis">
              <span class="dashboard-panel-emphasis-label">
                {{ $t("views.dashboard_home_page.today") }}
              </span>
              <strong>{{ currentAuthenticatedAgents }}</strong>
            </div>
          </header>
          <div class="dashboard-chart-wrap dashboard-chart-wrap-hero">
            <StateAgentsChartLine
              :chartLineInterval="chartLineIntervalAuth"
              :chartLineEventYesterdayData="chartLineAuthEventYesterdayData"
              :chartLineEventTodayData="chartLineAuthEventTodayData"
            />
          </div>
        </section>
      </div>

      <div class="col-12 xl:col-4">
        <section class="dashboard-panel dashboard-panel-side">
          <header class="dashboard-panel-header dashboard-panel-header-stacked">
            <div>
              <span class="dashboard-panel-kicker">
                {{ $t("views.dashboard_home_page.call_sumary") }}
              </span>
              <h3 class="dashboard-panel-title">
                {{ totalContactedCalls }}
              </h3>
            </div>
            <span class="dashboard-pill">
              {{ totalActiveCampaigns }}
            </span>
          </header>

          <div class="dashboard-highlight-grid">
            <div class="dashboard-highlight-card">
              <span class="dashboard-highlight-label">
                {{ $t("views.dashboard_home_page.authenticated_agents") }}
              </span>
              <strong>{{ currentAuthenticatedAgents }}</strong>
            </div>
            <div class="dashboard-highlight-card">
              <span class="dashboard-highlight-label">
                {{ $t("views.dashboard_home_page.califications") }}
              </span>
              <strong>{{ currentCalifications }}</strong>
            </div>
          </div>

          <div class="dashboard-breakdown">
            <div class="dashboard-breakdown-group">
              <h4>{{ $t("views.dashboard_home_page.call_sumary") }}</h4>
              <div
                v-for="metric in contactedMetrics"
                :key="metric.label"
                class="dashboard-breakdown-row"
              >
                <div class="dashboard-breakdown-main">
                  <span
                    class="dashboard-breakdown-dot"
                    :style="{ background: metric.color }"
                  ></span>
                  <span>{{ metric.label }}</span>
                </div>
                <strong>{{ metric.value }}</strong>
              </div>
            </div>

            <div class="dashboard-breakdown-group">
              <h4>{{ $t("views.dashboard_home_page.agent_status") }}</h4>
              <div
                v-for="metric in agentStateMetrics"
                :key="metric.label"
                class="dashboard-breakdown-row"
              >
                <div class="dashboard-breakdown-main">
                  <span
                    class="dashboard-breakdown-dot"
                    :style="{ background: metric.color }"
                  ></span>
                  <span>{{ metric.label }}</span>
                </div>
                <strong>{{ metric.value }}</strong>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div class="col-12 xl:col-8">
        <section class="dashboard-panel">
          <header class="dashboard-panel-header">
            <div>
              <span class="dashboard-panel-kicker">
                {{ $t("views.dashboard_home_page.today") }} / {{ $t("views.dashboard_home_page.yesterday") }}
              </span>
              <h3 class="dashboard-panel-title">
                {{ $t("views.dashboard_home_page.califications") }}
              </h3>
            </div>
            <div class="dashboard-panel-emphasis">
              <span class="dashboard-panel-emphasis-label">
                {{ $t("views.dashboard_home_page.today") }}
              </span>
              <strong>{{ currentCalifications }}</strong>
            </div>
          </header>
          <div class="dashboard-chart-wrap">
            <StateAgentsChartLine
              :chartLineInterval="chartLineIntervalCalification"
              :chartLineEventYesterdayData="chartLineCalificationEventYesterdayData"
              :chartLineEventTodayData="chartLineCalificationEventTodayData"
            />
          </div>
        </section>
      </div>

      <div class="col-12 xl:col-4">
        <section class="dashboard-panel">
          <header class="dashboard-panel-header">
            <div>
              <span class="dashboard-panel-kicker">
                {{ $t("views.dashboard_home_page.call_sumary") }}
              </span>
              <h3 class="dashboard-panel-title">
                {{ $t("views.dashboard_home_page.call_sumary") }}
              </h3>
            </div>
          </header>
          <div class="dashboard-chart-wrap dashboard-chart-wrap-donut">
            <ContactedCallsChart :chartData="reportData.contacted_calls" />
          </div>
        </section>
      </div>

      <div class="col-12">
        <section class="dashboard-panel">
          <header class="dashboard-panel-header">
            <div>
              <span class="dashboard-panel-kicker">
                {{ totalAgents }}
              </span>
              <h3 class="dashboard-panel-title">
                {{ $t("views.dashboard_home_page.agent_status") }}
              </h3>
            </div>
          </header>
          <div class="dashboard-chart-wrap dashboard-chart-wrap-bar">
            <StateAgentsChart :chartData="reportData.state_agents" />
          </div>
        </section>
      </div>
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
        resourceCounts: {
            type: Object,
            default: () => ({
                whatsappLines: 0,
                metaLandingPages: 0
            })
        },
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
    computed: {
        totalActiveCampaigns () {
            return this.sumValues(this.reportData.active_campaigns);
        },
        totalContactedCalls () {
            return this.sumValues(this.reportData.contacted_calls);
        },
        totalAgents () {
            return this.sumValues(this.reportData.state_agents);
        },
        currentAuthenticatedAgents () {
            return this.getLastMetricValue(this.chartLineAuthEventTodayData);
        },
        currentCalifications () {
            return this.getLastMetricValue(this.chartLineCalificationEventTodayData);
        },
        overviewMetrics () {
            return [
                {
                    label: this.$t('views.dashboard_home_page.authenticated_agents'),
                    value: this.currentAuthenticatedAgents,
                    color: '#5da3ff'
                },
                {
                    label: this.$t('views.dashboard_home_page.califications'),
                    value: this.currentCalifications,
                    color: '#ffb54d'
                },
                {
                    label: this.$t('views.dashboard_home_page.call_sumary'),
                    value: this.totalContactedCalls,
                    color: '#8FC641'
                }
            ];
        },
        resourceMetrics () {
            return [
                {
                    label: 'Lineas de Whatsapp',
                    value: Number(this.resourceCounts?.whatsappLines || 0),
                    color: '#25D366'
                },
                {
                    label: 'Meta Landing Pages',
                    value: Number(this.resourceCounts?.metaLandingPages || 0),
                    color: '#1877F2'
                }
            ];
        },
        contactedMetrics () {
            const colors = {
                attended: '#8FC641',
                failed: '#ff7b72'
            };
            return this.getMetricEntries(this.reportData.contacted_calls, 'call_sumary', colors);
        },
        agentStateMetrics () {
            const colors = {
                ready: '#7ce38b',
                oncall: '#5da3ff',
                pause: '#ffb54d'
            };
            return this.getMetricEntries(this.reportData.state_agents, 'agent_status', colors);
        }
    },
    methods: {
        sumValues (data = {}) {
            return Object.values(data || {}).reduce((total, value) => total + Number(value || 0), 0);
        },
        getLastMetricValue (data = []) {
            const validEntries = (data || []).filter(value => value !== null && value !== undefined);
            return validEntries.length ? validEntries[validEntries.length - 1] : 0;
        },
        getMetricEntries (data = {}, translationPrefix = '', colors = {}) {
            return Object.entries(data || {}).map(([key, value]) => {
                const translationKey = `views.dashboard_home_page.${translationPrefix}_${key}`;
                const translatedLabel = this.$t(translationKey);
                return {
                    key,
                    label: translatedLabel !== translationKey ? translatedLabel : this.titleize(key),
                    value: Number(value || 0),
                    color: colors[key] || '#5da3ff'
                };
            });
        },
        titleize (text = '') {
            return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
        }
    }
};
</script>

<style>
.dashboard-shell {
  --dashboard-surface: rgba(255, 255, 255, 0.95);
  --dashboard-surface-strong: #ffffff;
  --dashboard-border: rgba(15, 23, 42, 0.08);
  --dashboard-outline: rgba(15, 23, 42, 0.04);
  --dashboard-text: #162033;
  --dashboard-muted: #6a778b;
  --dashboard-shadow: 0 24px 60px rgba(15, 23, 42, 0.1);
  --dashboard-shell-bg:
    radial-gradient(circle at top left, rgba(93, 163, 255, 0.16), transparent 30%),
    radial-gradient(circle at top right, rgba(143, 198, 65, 0.16), transparent 35%),
    linear-gradient(180deg, #f5f7fb 0%, #edf2f8 100%);
  color: var(--dashboard-text);
  width: 100%;
  max-width: 100%;
  padding: 1rem;
  border-radius: 28px;
  background: var(--dashboard-shell-bg);
  overflow-x: hidden;
  box-sizing: border-box;
}

html.dark-mode .dashboard-shell {
  --dashboard-surface: rgba(18, 22, 33, 0.92);
  --dashboard-surface-strong: #171c28;
  --dashboard-border: rgba(255, 255, 255, 0.08);
  --dashboard-outline: rgba(255, 255, 255, 0.04);
  --dashboard-text: #f5f7fb;
  --dashboard-muted: #9aa8bf;
  --dashboard-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
  --dashboard-shell-bg:
    radial-gradient(circle at top left, rgba(93, 163, 255, 0.18), transparent 30%),
    radial-gradient(circle at top right, rgba(255, 181, 77, 0.16), transparent 32%),
    linear-gradient(180deg, #0d1118 0%, #121723 100%);
}

.dashboard-grid {
  margin-top: 0;
  margin-right: 0;
  margin-left: 0;
}

.dashboard-status-strip {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.dashboard-status-cluster {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.dashboard-status-cluster--right {
  margin-left: auto;
  justify-content: flex-end;
}

.dashboard-status-item {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.9rem 1rem;
  border-radius: 999px;
  background: var(--dashboard-surface);
  border: 1px solid var(--dashboard-border);
  box-shadow: var(--dashboard-shadow);
  backdrop-filter: blur(14px);
}

.dashboard-status-dot {
  width: 0.65rem;
  height: 0.65rem;
  border-radius: 999px;
  box-shadow: 0 0 0 0.3rem rgba(255, 255, 255, 0.08);
}

.dashboard-status-label {
  color: var(--dashboard-muted);
  font-size: 0.92rem;
}

.dashboard-status-value {
  font-size: 1rem;
  color: var(--dashboard-text);
}

@media (max-width: 960px) {
  .dashboard-status-cluster--right {
    margin-left: 0;
    justify-content: flex-start;
  }
}

.dashboard-panel {
  position: relative;
  height: 100%;
  padding: 1.15rem;
  border-radius: 26px;
  background: var(--dashboard-surface);
  border: 1px solid var(--dashboard-border);
  box-shadow: var(--dashboard-shadow);
  overflow: hidden;
}

.dashboard-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.24), transparent 40%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.dashboard-panel-hero {
  min-height: 24rem;
}

.dashboard-panel-side {
  min-height: 24rem;
}

.dashboard-panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.dashboard-panel-header-stacked {
  align-items: center;
}

.dashboard-panel-kicker {
  display: inline-block;
  margin-bottom: 0.4rem;
  color: var(--dashboard-muted);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.dashboard-panel-title {
  margin: 0;
  font-size: 1.4rem;
  line-height: 1.2;
  color: var(--dashboard-text);
}

.dashboard-panel-emphasis {
  min-width: 5.5rem;
  padding: 0.85rem 1rem;
  border-radius: 18px;
  text-align: right;
  background: rgba(93, 163, 255, 0.12);
  border: 1px solid rgba(93, 163, 255, 0.18);
}

html.dark-mode .dashboard-panel-emphasis {
  background: rgba(93, 163, 255, 0.14);
}

.dashboard-panel-emphasis-label {
  display: block;
  margin-bottom: 0.3rem;
  color: var(--dashboard-muted);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.dashboard-panel-emphasis strong {
  font-size: 1.5rem;
  color: var(--dashboard-text);
}

.dashboard-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 3rem;
  height: 3rem;
  padding: 0 0.9rem;
  border-radius: 999px;
  font-weight: 700;
  color: var(--dashboard-text);
  background: rgba(143, 198, 65, 0.16);
  border: 1px solid rgba(143, 198, 65, 0.2);
}

.dashboard-highlight-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
  margin-bottom: 1.35rem;
}

.dashboard-highlight-card {
  padding: 1rem;
  border-radius: 20px;
  background: var(--dashboard-surface-strong);
  border: 1px solid var(--dashboard-outline);
}

html.dark-mode .dashboard-highlight-card {
  background: rgba(255, 255, 255, 0.03);
}

.dashboard-highlight-label {
  display: block;
  margin-bottom: 0.55rem;
  color: var(--dashboard-muted);
  font-size: 0.9rem;
}

.dashboard-highlight-card strong {
  font-size: 1.85rem;
  color: var(--dashboard-text);
}

.dashboard-breakdown {
  display: grid;
  gap: 1rem;
}

.dashboard-breakdown-group {
  padding: 1rem;
  border-radius: 20px;
  background: var(--dashboard-surface-strong);
  border: 1px solid var(--dashboard-outline);
}

html.dark-mode .dashboard-breakdown-group {
  background: rgba(255, 255, 255, 0.03);
}

.dashboard-breakdown-group h4 {
  margin: 0 0 0.85rem;
  color: var(--dashboard-text);
  font-size: 0.96rem;
}

.dashboard-breakdown-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.65rem 0;
  border-top: 1px solid var(--dashboard-border);
}

.dashboard-breakdown-row:first-of-type {
  border-top: 0;
  padding-top: 0;
}

.dashboard-breakdown-main {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  color: var(--dashboard-muted);
}

.dashboard-breakdown-row strong {
  color: var(--dashboard-text);
}

.dashboard-breakdown-dot {
  width: 0.7rem;
  height: 0.7rem;
  border-radius: 999px;
}

.dashboard-chart-wrap {
  height: 17rem;
}

.dashboard-chart-wrap-hero {
  height: 17.5rem;
}

.dashboard-chart-wrap-donut {
  height: 16rem;
}

.dashboard-chart-wrap-bar {
  height: 16rem;
}

@media screen and (max-width: 991px) {
  .dashboard-shell {
    padding: 0.85rem;
    border-radius: 20px;
  }

  .dashboard-panel,
  .dashboard-panel-hero,
  .dashboard-panel-side {
    min-height: auto;
  }

  .dashboard-highlight-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-panel-header {
    flex-direction: column;
  }

  .dashboard-panel-emphasis {
    width: 100%;
    text-align: left;
  }

  .dashboard-chart-wrap,
  .dashboard-chart-wrap-hero,
  .dashboard-chart-wrap-donut,
  .dashboard-chart-wrap-bar {
    height: 17rem;
  }
}
</style>
