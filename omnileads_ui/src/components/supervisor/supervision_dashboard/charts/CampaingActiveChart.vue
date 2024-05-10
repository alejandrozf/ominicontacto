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
            alueColor="#fffff"
            rangeColor="#8FC641"
          />
        </div>
      </div>
    </template>
  </Card>
</template>
<script>
import { computed } from 'vue';

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
        const basicData = computed(() => {
            return {
                value: props.chartData
            };
        });
        return {
            basicData
        };
    }
};
</script>
