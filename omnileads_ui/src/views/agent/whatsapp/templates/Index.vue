<template>
  <div>
    <Header @handleClearFiltersEvent="clearFiltersEvent" />
    <Table
      ref="tableRef"
      @handleModalEvent="handleModal"
      :onlyWhatappTemplates="onlyWhatappTemplates"
    />
    <ModalTemplateParams
      :showModal="showModal"
      :template="template"
      :conversationId="conversationId"
      :onlyWhatappTemplates="onlyWhatappTemplates"
      @handleModalEvent="handleModal"
    />
  </div>
</template>

<script>
import Header from '@/components/agent/whatsapp/templates/Header';
import Table from '@/components/agent/whatsapp/templates/Table';
import ModalTemplateParams from '@/components/agent/whatsapp/templates/ModalTemplateParams';
import { mapActions, mapState } from 'vuex';
export default {
    components: {
        Header,
        Table,
        ModalTemplateParams
    },
    data () {
        return {
            showModal: false,
            template: null,
            conversationId: null,
            campaignId: null,
            conversationInfo: null,
            onlyWhatappTemplates: false
        };
    },
    mounted () {
        window.addEventListener('storage', this.updatedLocalStorage);
        this.updatedLocalStorage();
    },
    beforeUnmount () {
        window.removeEventListener('storage', this.updatedLocalStorage);
    },
    computed: {
        ...mapState(['agtWhatsCoversationInfo'])
    },
    methods: {
        ...mapActions(['initSupCampaignTemplates', 'agtWhatsSetCoversationInfo']),
        clearFiltersEvent () {
            this.$refs.tableRef.clearFilter();
        },
        handleModal ({ showModal = false, template = null, conversationId = null }) {
            this.showModal = showModal;
            this.template = template;
            this.conversationId = conversationId;
        },
        updatedLocalStorage () {
            this.conversationInfo =
        JSON.parse(localStorage.getItem('agtWhatsCoversationInfo')) || null;
            this.onlyWhatappTemplates =
        localStorage.getItem('onlyWhatappTemplates').toString() === 'true';
            this.agtWhatsSetCoversationInfo(this.conversationInfo);
            this.conversationId = this.conversationInfo
                ? parseInt(this.conversationInfo.id)
                : null;
            this.campaignId = this.conversationInfo
                ? parseInt(this.conversationInfo.campaignId)
                : null;
            if (this.campaignId) {
                this.initSupCampaignTemplates(this.campaignId);
            }
        }
    }
};
</script>
