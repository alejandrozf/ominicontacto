<template>
  <div>
    <Header @handleClearFiltersEvent="clearFiltersEvent" />
    <Table ref="tableRef" @handleModalEvent="handleModal" />
    <ModalTemplateParams
      :showModal="showModal"
      :template="template"
      :conversationId="conversationId"
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
            campaignId: null
        };
    },
    mounted () {
        window.addEventListener('storage', this.updatedLocalStorage);
        this.updatedLocalStorage();
    },
    beforeUnmount () {
        window.removeEventListener(
            'storage',
            this.updatedLocalStorage
        );
    },
    computed: {
        ...mapState(['agtWhatsCoversationInfo'])
    },
    methods: {
        ...mapActions(['initSupCampaignTemplates', 'agtWhatsSetCoversationId']),
        clearFiltersEvent () {
            this.$refs.tableRef.clearFilter();
        },
        handleModal ({ showModal = false, template = null, conversationId = null }) {
            this.showModal = showModal;
            this.template = template;
            this.conversationId = conversationId;
        },
        updatedLocalStorage () {
            this.conversationId = localStorage.getItem('agtWhatsappConversationId') || null;
            this.campaignId = localStorage.getItem('agtWhatsCoversationCampaignId') || null;
            if (this.campaignId) {
                this.initSupCampaignTemplates(this.campaignId);
            }
            if (this.conversationId) {
                this.agtWhatsSetCoversationId(this.conversationId);
            }
        }
    }
};
</script>
