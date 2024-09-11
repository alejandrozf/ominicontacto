<template>
  <div>
    <Header
      @handleCloseEvent="closeEvent"
      :title="
        formToCreate||formToCreateFromNewConversation
          ? $t('views.whatsapp.contact.new')
          : $t('views.whatsapp.contact.edit')
      "
    />
    <Form
      ref="formRef"
      @cleanFilterSearchEvent="cleanFilterSearch"
      :formToCreate="formToCreate"
      :formToCreateFromNewConversation="formToCreateFromNewConversation"
      :previewContact="previewContact"
    />
  </div>
</template>

<script>
import Header from '@/components/agent/whatsapp/contact/Header';
import Form from '@/components/agent/whatsapp/contact/Form';
import SearchTable from '@/components/agent/whatsapp/contact/SearchTable';
import { WHATSAPP_LOCALSTORAGE_EVENTS } from '@/globals/agent/whatsapp';
import { HTTP_STATUS } from '@/globals';
import { mapActions } from 'vuex';
export default {
    inject: ['$helpers'],
    components: {
        Header,
        Form,
        SearchTable
    },
    data () {
        return {
            conversationInfo: null,
            formToCreate: null,
            formToCreateFromNewConversation: null,
            previewContact: null,
            inconmingConversation: false
        };
    },
    methods: {
        ...mapActions([
            'agtWhatsContactDBFieldsInit',
            'agtWhatsSetCoversationInfo'
        ]),
        cleanFilterSearch () {
            this.previewContact = null;
        },
        selectPreviewContact (contact) {
            this.previewContact = contact;
        },
        closeEvent () {
            this.$refs.formRef.clearForm();
        },
        async updatedLocalStorage () {
            const agtWhatsCoversationInfo = localStorage.getItem('agtWhatsCoversationInfo');
            if (agtWhatsCoversationInfo && agtWhatsCoversationInfo !== 'null') {
                this.conversationInfo = JSON.parse(agtWhatsCoversationInfo);
                this.formToCreate = this.conversationInfo.client.id === null
                this.agtWhatsSetCoversationInfo(this.conversationInfo);
                this.$helpers.openLoader(this.$t);
                const { status, message } = await this.agtWhatsContactDBFieldsInit({
                    campaignId: this.conversationInfo.campaignId,
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
            } else {
                this.formToCreateFromNewConversation = true
                const { status, message } = await this.agtWhatsContactDBFieldsInit({
                    campaignId: localStorage.getItem('agtWhatsCampaingId'),
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
            this.inconmingConversation = localStorage.getItem('agtWhatsInconmingConversation') === 'true';
        }
    },
    mounted () {
        window.parent.document.addEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.CONTACT.FORM_INIT_DATA,
            this.updatedLocalStorage
        );
    },
    beforeUnmount () {
        window.parent.document.removeEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.CONTACT.FORM_INIT_DATA,
            this.updatedLocalStorage
        );
    },
    async created () {
        await this.updatedLocalStorage();
    }
};
</script>
