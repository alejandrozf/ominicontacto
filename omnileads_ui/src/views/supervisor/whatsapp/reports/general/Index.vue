<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.whatsapp.reports.general.title") }}</h1>
      </template>
    </Toolbar>
    <div class="mx-4">
      <FilterForm :campaignId="campaignId" ref="formFilters" />
      <Dashboard @cleanFiltersEvent="cleanFilters()" class="mt-4" />
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import Dashboard from '@/components/supervisor/whatsapp/reports/general/Dashboard';
import FilterForm from '@/components/supervisor/whatsapp/reports/general/FilterForm';

export default {
    inject: ['$helpers'],
    data () {
        return {
            campaignId: null,
            showModal: false
        };
    },
    components: {
        FilterForm,
        Dashboard
    },
    async created () {
        const element = window.parent.document.getElementById('campaignId');
        this.campaignId = element ? element.value : null;
        const { rgbColors, rgbaColors } = this.$helpers.getRandomColors(12);
        await this.initSupWhatsReportGeneralColors({ rgbColors, rgbaColors });
    },
    methods: {
        ...mapActions(['initSupWhatsReportGeneralColors']),
        cleanFilters () {
            this.$refs.formFilters.cleanFilters();
        }
    }
};
</script>
