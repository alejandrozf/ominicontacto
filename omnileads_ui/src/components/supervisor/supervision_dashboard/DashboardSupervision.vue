<template>
  <div
    v-if="reportData.data === null"
    class="dashboard-loading-shell"
  >
    <div class="dashboard-loading-card">
      <span class="dashboard-loading-spinner"></span>
      <strong class="dashboard-loading-title">Cargando dashboard</strong>
      <span class="dashboard-loading-text">
        Preparando indicadores, campañas y actividad reciente.
      </span>
    </div>
  </div>
  <DashboardSupervisionDetail
    v-else
    :reportData="reportData.data"
    :resourceCounts="resourceCounts"
    :chartLineIntervalAuth="chartLineIntervalAuth"
    :chartLineAuthEventYesterdayData="chartLineAuthEventYesterdayData"
    :chartLineAuthEventTodayData="chartLineAuthEventTodayData"
    :chartLineIntervalCalification="chartLineIntervalCalification"
    :chartLineCalificationEventYesterdayData="chartLineCalificationEventYesterdayData"
    :chartLineCalificationEventTodayData="chartLineCalificationEventTodayData"
  >
  </DashboardSupervisionDetail>
</template>
<script>
import { watch, ref, onMounted } from 'vue';
import { useWebSocket } from '@vueuse/core';
import apiUrls from '@/api_urls/supervisor';

import { apiCall } from '@/hooks/apiCall';
import DashboardSupervisionDetail from '@/components/supervisor/supervision_dashboard/DashboardSupervisionDetail.vue';
import LineService from '@/services/supervisor/whatsapp/line_service';
import PageService from '@/services/supervisor/facebook/page_service';

export default {
    components: {
        DashboardSupervisionDetail
    },
    setup () {
        const lineService = new LineService();
        const pageService = new PageService();

        function getCollectionSize (response) {
            const items = response?.data;
            return Array.isArray(items) ? items.length : 0;
        }

        async function fetchResourceCounts () {
            try {
                const [linesResponse, pagesResponse] = await Promise.all([
                    lineService.list(),
                    pageService.list()
                ]);
                resourceCounts.value = {
                    whatsappLines: getCollectionSize(linesResponse),
                    metaLandingPages: getCollectionSize(pagesResponse)
                };
            } catch (error) {
                console.error('Error al obtener los contadores del dashboard');
                console.error(error);
                resourceCounts.value = {
                    whatsappLines: 0,
                    metaLandingPages: 0
                };
            }
        }

        function getAuthEventData (interval, eventList, caseType, language = window.navigator.language) {
            const data = [];
            const ranges = [];
            var date = new Date();
            if (caseType !== 'today') {
                date.setDate(date.getDate() - 1);
            }
            const format = {
                hour: 'numeric',
                minute: 'numeric'
            };
            let eventListIndex = 0;
            let eventCount = 0;
            for (let minutes = 0; minutes < 24 * 60; minutes = minutes + interval) {
                date.setHours(0);
                date.setMinutes(minutes);
                ranges.push(date.toLocaleTimeString(language, format));
                const now = Date.now();
                while (eventListIndex < eventList.length) {
                    const eventCurrent = eventList[eventListIndex];
                    const eventTime = new Date(eventCurrent.timestamp * 1000);
                    if (date < eventTime) { break; } // no analizar eventos con mayor fecha del rango que estoy analizando
                    const difMinutes = Math.floor((date - eventTime) / 60000);
                    if (difMinutes <= interval) {
                        eventCount = eventCurrent.actives;
                    }
                    eventListIndex++;
                }
                data.push(eventCount);
                if (caseType === 'today' && date > new Date(Math.floor(now / 1000) * 1000)) { break; }
            }
            return { ranges, data };
        }
        function getCalificationEventData (interval, eventList, caseType, language = window.navigator.language) {
            const data = [];
            const ranges = [];
            var date = new Date();
            if (caseType !== 'today') {
                date.setDate(date.getDate() - 1);
            }
            const format = {
                hour: 'numeric',
                minute: 'numeric'
            };
            let eventListIndex = 0;
            let eventCount = 0;
            for (let minutes = 0; minutes < 24 * 60; minutes = minutes + interval) {
                date.setHours(0);
                date.setMinutes(minutes);
                ranges.push(date.toLocaleTimeString(language, format));
                const now = Date.now();
                while (eventListIndex < eventList.length) {
                    const eventCurrent = eventList[eventListIndex];
                    const eventTime = new Date(eventCurrent.timestamp * 1000);
                    if (date < eventTime) { break; } // no analizar eventos con mayor fecha del rango que estoy analizando
                    const difMinutes = Math.floor((date - eventTime) / 60000);
                    if (difMinutes <= interval) {
                        eventCount = eventCount + 1;
                    }
                    eventListIndex++;
                }
                data.push(eventCount);
                if (caseType === 'today' && date > new Date(Math.floor(now / 1000) * 1000)) { break; }
            }
            return { ranges, data };
        }
        var today = new Date();
        var yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        today = today.toISOString().slice(0, 10);
        yesterday = yesterday.toISOString().slice(0, 10);

        const authEventYesterdayList = [];
        const authEventTodayList = [];
        const calificationEventYesterdayList = [];
        const calificationTodayList = [];

        const urlYesterdayAuth = `wss://${window.location.host}/consumers/stream/auth_event_${yesterday}`;
        const urlTodayAuth = `wss://${window.location.host}/consumers/stream/auth_event_${today}`;

        const urlYesterdayCalification = `wss://${window.location.host}/consumers/stream/calification_event_${yesterday}`;
        const urlTodayCalificaction = `wss://${window.location.host}/consumers/stream/calification_event_${today}`;

        const chartLineAuthEventYesterdayData = ref([]);
        const chartLineAuthEventTodayData = ref([]);
        const chartLineIntervalAuth = ref([]);

        const chartLineCalificationEventYesterdayData = ref([]);
        const chartLineCalificationEventTodayData = ref([]);
        const chartLineIntervalCalification = ref([]);

        const loadingData = ref(false);
        const reportData = ref({ data: null });
        const resourceCounts = ref({
            whatsappLines: 0,
            metaLandingPages: 0
        });
        const { loading, response } = apiCall(apiUrls.DashboardSupervision);
        watch(loading, () => {
            loadingData.value = loading.value;
            reportData.value = response.value;
        });
        onMounted(() => {
            fetchResourceCounts();
        });
        useWebSocket(urlYesterdayAuth, {
            autoReconnect: true,
            onMessage (ws, event) {
                if (event.data !== 'Stream subscribed!') {
                    const events = JSON.parse(event.data);
                    events.forEach(element => {
                        authEventYesterdayList.push(JSON.parse(element.replaceAll('\'', '"')));
                    });
                    const getEventDataResponse = getAuthEventData(5, authEventYesterdayList, 'yesterday');
                    chartLineIntervalAuth.value = getEventDataResponse.ranges;
                    chartLineAuthEventYesterdayData.value = getEventDataResponse.data;
                    // close();
                }
            }
        });
        useWebSocket(urlTodayAuth, {
            autoReconnect: true,
            onMessage (ws, event) {
                if (event.data !== 'Stream subscribed!') {
                    const events = JSON.parse(event.data);
                    events.forEach(element => {
                        authEventTodayList.push(JSON.parse(element.replaceAll('\'', '"')));
                    });
                    const getEventDataResponse = getAuthEventData(5, authEventTodayList, 'today');
                    if (chartLineIntervalAuth.value.length === 0) {
                        chartLineIntervalAuth.value = getEventDataResponse.ranges;
                    }
                    chartLineAuthEventTodayData.value = getEventDataResponse.data;
                }
            }
        });

        useWebSocket(urlYesterdayCalification, {
            autoReconnect: true,
            onMessage (ws, event) {
                if (event.data !== 'Stream subscribed!') {
                    const events = JSON.parse(event.data);
                    events.forEach(element => {
                        calificationEventYesterdayList.push(JSON.parse(element.replaceAll('\'', '"')));
                    });
                    const getEventDataResponse = getCalificationEventData(60, calificationEventYesterdayList, 'yesterday');
                    chartLineIntervalCalification.value = getEventDataResponse.ranges;
                    chartLineCalificationEventYesterdayData.value = getEventDataResponse.data;
                    // close2();
                }
            }
        });
        useWebSocket(urlTodayCalificaction, {
            autoReconnect: true,
            onMessage (ws, event) {
                if (event.data !== 'Stream subscribed!') {
                    const events = JSON.parse(event.data);
                    events.forEach(element => {
                        calificationTodayList.push(JSON.parse(element.replaceAll('\'', '"')));
                    });
                    const getEventDataResponse = getCalificationEventData(60, calificationTodayList, 'today');
                    if (chartLineIntervalCalification.value.length === 0) {
                        chartLineIntervalCalification.value = getEventDataResponse.ranges;
                    }
                    chartLineCalificationEventTodayData.value = getEventDataResponse.data;
                }
            }
        });
        setInterval(function () {
            const { loading, response } = apiCall(apiUrls.DashboardSupervision);
            watch(loading, () => {
                loadingData.value = loading.value;
                reportData.value = response.value;
            });
            fetchResourceCounts();
            const getEventDataResponse = getCalificationEventData(60, calificationTodayList, 'today');
            if (chartLineIntervalCalification.value.length === 0) {
                chartLineIntervalCalification.value = getEventDataResponse.ranges;
            }
            chartLineCalificationEventTodayData.value = getEventDataResponse.data;
        }, 60000);
        return {
            chartLineIntervalAuth,
            chartLineAuthEventYesterdayData,
            chartLineAuthEventTodayData,

            chartLineIntervalCalification,
            chartLineCalificationEventYesterdayData,
            chartLineCalificationEventTodayData,

            loadingData,
            reportData,
            resourceCounts
        };
    }

};
</script>
<style>
.dashboard-loading-shell {
  min-height: 34rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  border-radius: 28px;
  background:
    radial-gradient(circle at top left, rgba(93, 163, 255, 0.16), transparent 30%),
    radial-gradient(circle at top right, rgba(143, 198, 65, 0.16), transparent 35%),
    linear-gradient(180deg, #f5f7fb 0%, #edf2f8 100%);
}

html.dark-mode .dashboard-loading-shell {
  background:
    radial-gradient(circle at top left, rgba(93, 163, 255, 0.18), transparent 30%),
    radial-gradient(circle at top right, rgba(255, 181, 77, 0.16), transparent 32%),
    linear-gradient(180deg, #0d1118 0%, #121723 100%);
}

.dashboard-loading-card {
  display: grid;
  justify-items: center;
  gap: 0.7rem;
  min-width: min(100%, 20rem);
  padding: 2.2rem 2rem;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
  text-align: center;
}

html.dark-mode .dashboard-loading-card {
  background: rgba(18, 22, 33, 0.92);
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
}

.dashboard-loading-spinner {
  width: 3.1rem;
  height: 3.1rem;
  border-radius: 999px;
  border: 3px solid rgba(93, 163, 255, 0.14);
  border-top-color: #5da3ff;
  border-right-color: #8fc641;
  animation: dashboard-spin 0.85s linear infinite;
}

.dashboard-loading-title {
  color: #162033;
  font-size: 1.15rem;
}

html.dark-mode .dashboard-loading-title {
  color: #f5f7fb;
}

.dashboard-loading-text {
  max-width: 18rem;
  color: #6a778b;
  font-size: 0.95rem;
  line-height: 1.5;
}

html.dark-mode .dashboard-loading-text {
  color: #9aa8bf;
}

@keyframes dashboard-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
