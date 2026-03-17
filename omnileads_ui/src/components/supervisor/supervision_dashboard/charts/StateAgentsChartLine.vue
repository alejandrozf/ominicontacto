<template>
    <div>
        <Chart type="line" :data="basicData" :options="basicOptions" :height="50" />
    </div>
 </template>

<script>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';

export default {
    props: {
        chartNameHoy: String,
        chartNameAyer: String,
        chartLineInterval: Object,
        chartLineEventYesterdayData: Object,
        chartLineEventTodayData: Object
    },
    setup (props) {
        const { t } = useI18n();
        const isDark = ref(false);

        let observer = null;
        onMounted(() => {
            isDark.value = document.documentElement.classList.contains('dark-mode');
            observer = new MutationObserver(() => {
                isDark.value = document.documentElement.classList.contains('dark-mode');
            });
            observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
        });
        
        onUnmounted(() => {
            if (observer) observer.disconnect();
        });

        const textColor = computed(() => isDark.value ? '#f2f3f5' : '#495057');
        const gridColor = computed(() => isDark.value ? 'rgba(255,255,255,0.05)' : '#ebedef');

        const basicData = computed(() => {
            return {
                labels: props.chartLineInterval,
                datasets: [
                    {
                        label: t('views.dashboard_home_page.today'),
                        data: props.chartLineEventTodayData,
                        fill: false,
                        borderColor: '#42A5F5'
                    },
                    {
                        label: t('views.dashboard_home_page.yesterday'),
                        data: props.chartLineEventYesterdayData,
                        fill: false,
                        borderColor: '#FFA726'
                    }
                ]
            };
        });

        const basicOptions = computed(() => {
            return {
                animation: {
                    duration: 0
                },
                plugins: {
                    legend: {
                        labels: {
                            color: textColor.value
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: textColor.value
                        },
                        grid: {
                            color: gridColor.value
                        }
                    },
                    y: {
                        ticks: {
                            color: textColor.value,
                            stepSize: 1
                        },
                        grid: {
                            color: gridColor.value
                        }
                    }
                }
            };
        });

        return { basicData, basicOptions };
    }
};
</script>
