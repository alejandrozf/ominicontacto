<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>Conversaciones Meta/Facebook</h1>
      </template>
    </Toolbar>
    <div class="mx-4">
      <FilterForm :campaignId="campaignId" ref="formFilters" />
      <ReportTable @cleanFiltersEvent="cleanFilters()" @handleModalEvent="handleModal" class="mt-4" />
    </div>
    <ModalConversationDetail
      :showModal="showModal"
      @handleModalEvent="handleModal"
    />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import ReportTable from '@/components/supervisor/facebook/reports/campaign/conversation_report/Table';
import FilterForm from '@/components/supervisor/facebook/reports/campaign/conversation_report/FilterForm';
import ModalConversationDetail from '@/components/supervisor/facebook/reports/campaign/conversation_report/ModalConversationDetail';

export default {
    data () {
        return {
            campaignId: null,
            showModal: false
        };
    },
    components: {
        ReportTable,
        FilterForm,
        ModalConversationDetail
    },
    async created () {
        const element = window.parent.document.getElementById('campaignId');
        this.campaignId = element ? parseInt(element.value) : null;
        await this.initSupFacebookReportCampaignAgents({
            campaignId: this.campaignId
        });
    },
    methods: {
        ...mapActions(['initSupFacebookReportCampaignAgents']),
        cleanFilters () {
            this.$refs.formFilters.cleanFilters();
        },
        handleModal ({ showModal = false }) {
            this.showModal = showModal;
        }
    }
};
</script>
