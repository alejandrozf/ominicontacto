<template>
  <div>
    <Header @handleClearFiltersEvent="clearFiltersEvent" />
    <Table
      ref="tableRef"
      @handleModalEvent="handleModal"
      :onlyWhatsappTemplates="onlyWhatsappTemplates"
    />
    <ModalTemplateParams
      :showModal="showModal"
      :template="template"
      :conversationId="conversationId"
      :onlyWhatsappTemplates="onlyWhatsappTemplates"
      @handleModalEvent="handleModal"
    />
  </div>
</template>

<script>
import Header from '@/components/agent/whatsapp/templates/Header';
import Table from '@/components/agent/whatsapp/templates/Table';
import ModalTemplateParams from '@/components/agent/whatsapp/templates/ModalTemplateParams';
import { WHATSAPP_LOCALSTORAGE_EVENTS } from '@/globals/agent/whatsapp';
import { mapActions, mapState } from 'vuex';
import { HTTP_STATUS } from '@/globals';
export default {
    inject: ['$helpers'],
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
            onlyWhatsappTemplates: false
        };
    },
    async created () {
        await this.updatedLocalStorage();
    },
    mounted () {
        window.parent.document.addEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.TEMPLATES_INIT_EVENT,
            this.updatedLocalStorage
        );
    },
    beforeUnmount () {
        window.parent.document.removeEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.TEMPLATES_INIT_EVENT,
            this.updatedLocalStorage
        );
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
        async updatedLocalStorage () {
            this.conversationInfo =
        JSON.parse(localStorage.getItem('agtWhatsCoversationInfo')) || null;
            this.onlyWhatsappTemplates =
        localStorage.getItem('onlyWhatsappTemplates')?.toString() === 'true';
            this.agtWhatsSetCoversationInfo(this.conversationInfo);
            this.conversationId = this.conversationInfo?.id
                ? parseInt(this.conversationInfo?.id)
                : null;
            this.campaignId = this.conversationInfo?.campaignId
                ? parseInt(this.conversationInfo?.campaignId)
                : null;
            const line = this.conversationInfo?.line || null;
            if (this.campaignId) {
                this.$helpers.openLoader(this.$t);
                const { status, message } = await this.initSupCampaignTemplates({
                    campaignId: this.campaignId,
                    lineId: line ? line.id : null
                });
                this.$helpers.closeLoader();
                if (status !== HTTP_STATUS.SUCCESS) {
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.error_notification'),
                            message,
                            this.$t('globals.icon_error')
                        )
                    );
                }
            }
        }
    }
};
</script>
