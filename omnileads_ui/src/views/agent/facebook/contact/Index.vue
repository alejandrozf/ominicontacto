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
import Header from '@/components/agent/facebook/contact/Header';
import Form from '@/components/agent/facebook/contact/Form';
import SearchTable from '@/components/agent/facebook/contact/SearchTable';
import { FACEBOOK_LOCALSTORAGE_EVENTS } from '@/globals/agent/facebook';
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
            'agtFacebookContactDBFieldsInit',
            'agtFacebookSetConversationInfo'
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
            const agtFacebookConversationInfo = localStorage.getItem('agtFacebookConversationInfo');
            if (agtFacebookConversationInfo && agtFacebookConversationInfo !== 'null') {
                this.conversationInfo = JSON.parse(agtFacebookConversationInfo);
                this.formToCreate = this.conversationInfo.client.id === null;
                this.formToCreateFromNewConversation = false;
                this.agtFacebookSetConversationInfo(this.conversationInfo);
                this.$helpers.openLoader(this.$t);
                const { status, message } = await this.agtFacebookContactDBFieldsInit({
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
                const { status, message } = await this.agtFacebookContactDBFieldsInit({
                    campaignId: localStorage.getItem('agtFacebookCampaingId'),
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
            this.inconmingConversation = localStorage.getItem('agtFacebookInconmingConversation') === 'true';
        }
    },
    mounted () {
        window.parent.document.addEventListener(
            FACEBOOK_LOCALSTORAGE_EVENTS.CONTACT.FORM_INIT_DATA,
            this.updatedLocalStorage
        );
    },
    beforeUnmount () {
        window.parent.document.removeEventListener(
            FACEBOOK_LOCALSTORAGE_EVENTS.CONTACT.FORM_INIT_DATA,
            this.updatedLocalStorage
        );
    },
    async created () {
        await this.updatedLocalStorage();
    }
};
</script>
