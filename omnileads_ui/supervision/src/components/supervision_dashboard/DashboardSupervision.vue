<template>
  <DashboardSupervisionDetail
    v-if="reportData.data !== null"
    :reportData="reportData.data"
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
import { watch, ref } from 'vue';
import { useWebSocket } from '@vueuse/core';
import apiUrls from '@/const';

import { apiCall } from '@/hooks/apiCall';
import DashboardSupervisionDetail from '@/components/supervision_dashboard/DashboardSupervisionDetail.vue';

export default {
    components: {
        DashboardSupervisionDetail
    },
    setup () {
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
        const { loading, response } = apiCall(apiUrls.DashboardSupervision);
        watch(loading, () => {
            loadingData.value = loading.value;
            reportData.value = response.value;
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
            reportData
        };
    }

};
</script>
