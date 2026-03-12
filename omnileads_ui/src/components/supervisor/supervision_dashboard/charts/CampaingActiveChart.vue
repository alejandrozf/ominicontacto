<template>
  <Card>
    <template #title>
      <h5 class="text-center">
        {{
          $t("views.dashboard_home_page.active_campaign_by_type", {
            type: titleize(chartName),
          })
        }}
      </h5>
    </template>
    <template #content>
      <div class="flex justify-content-center flex-wrap">
        <div class="flex align-items-center justify-content-center">
          <Knob
            v-model="basicData.value"
            readonly
            :min="0"
            :max="500"
            :size="150"
            :valueColor="activeColor"
            :rangeColor="trackColor"
          />
        </div>
      </div>
    </template>
  </Card>
</template>
<script>
import { computed, ref, onMounted, onUnmounted } from 'vue';

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

        const trackColor = computed(() => isDark.value ? 'rgba(255,255,255,0.1)' : '#ebedef');
        const activeColor = computed(() => '#8FC641');

        const basicData = computed(() => {
            return {
                value: props.chartData
            };
        });
        
        return {
            basicData,
            trackColor,
            activeColor
        };
    }
};
</script>
