<template>
  <div class="grid align-content-center">
    <div
      class="field sm:col-12 md:col-12 lg:col-6 xl:col-6 flex justify-content-center"
    >
      <Doughnut :labels="labels" :colors="colors" :data="data" />
    </div>
    <div
      class="field sm:col-12 md:col-12 lg:col-6 xl:col-6 flex justify-content-center"
    >
      <PolarArea :labels="labels" :colors="colors" :data="data" />
    </div>
    <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
      <Line :labels="labels" :colors="colors" :data="data" />
    </div>
    <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
      <Bar :labels="labels" :colors="colors" :data="data" />
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import Doughnut from '@/components/supervisor/whatsapp/reports/general/graphics/Doughnut';
import Line from '@/components/supervisor/whatsapp/reports/general/graphics/Line';
import Bar from '@/components/supervisor/whatsapp/reports/general/graphics/Bar';
import PolarArea from '@/components/supervisor/whatsapp/reports/general/graphics/PolarArea';

export default {
    data () {
        return {
            labels: [],
            colors: {
                rgbColors: [],
                rgbaColors: []
            },
            data: []
        };
    },
    components: {
        Doughnut,
        PolarArea,
        Line,
        Bar
    },
    created () {
        this.labels = [
            this.$t('views.whatsapp.reports.general.sent_messages'),
            this.$t('views.whatsapp.reports.general.received_messages'),
            this.$t('views.whatsapp.reports.general.interactions_started'),
            this.$t('views.whatsapp.reports.general.attended_chats'),
            this.$t('views.whatsapp.reports.general.not_attended_chats'),
            this.$t('views.whatsapp.reports.general.inbound_chats_attended'),
            this.$t('views.whatsapp.reports.general.inbound_chats_not_attended'),
            this.$t('views.whatsapp.reports.general.inbound_chats_expired'),
            this.$t('views.whatsapp.reports.general.outbound_chats_attended'),
            this.$t('views.whatsapp.reports.general.outbound_chats_not_attended'),
            this.$t('views.whatsapp.reports.general.outbound_chats_expired'),
            this.$t('views.whatsapp.reports.general.outbound_chats_failed')
        ];
    },
    computed: {
        ...mapState(['supFacebookReportGeneralColors', 'supFacebookReportGeneral'])
    },
    watch: {
        supFacebookReportGeneralColors: {
            handler () {
                this.colors.rgbColors = this.supFacebookReportGeneralColors.rgbColors;
                this.colors.rgbaColors = this.supFacebookReportGeneralColors.rgbaColors;
            },
            deep: true,
            immediate: true
        },
        supFacebookReportGeneral: {
            handler () {
                this.data = [];
                for (const key in this.supFacebookReportGeneral) {
                    this.data.push(this.supFacebookReportGeneral[key]);
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
