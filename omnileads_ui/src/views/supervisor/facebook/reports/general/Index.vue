<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>Reportes Meta/Facebook</h1>
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
import Dashboard from '@/components/supervisor/facebook/reports/general/Dashboard';
import FilterForm from '@/components/supervisor/facebook/reports/general/FilterForm';

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
        this.campaignId = element ? parseInt(element.value) : null;
        const { rgbColors, rgbaColors } = this.$helpers.getRandomColors(12);
        await this.initSupFacebookReportGeneralColors({ rgbColors, rgbaColors });
    },
    methods: {
        ...mapActions(['initSupFacebookReportGeneralColors']),
        cleanFilters () {
            this.$refs.formFilters.cleanFilters();
        }
    }
};
</script>
