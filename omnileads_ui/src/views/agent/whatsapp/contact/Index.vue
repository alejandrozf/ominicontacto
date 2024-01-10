<template>
  <div>
    <Header
      @handleCloseEvent="closeEvent"
      :title="
        formToCreate
          ? $t('views.whatsapp.contact.new')
          : $t('views.whatsapp.contact.edit')
      "
    />
    <Form ref="formRef" :formToCreate="formToCreate" />
  </div>
</template>

<script>
import Header from '@/components/agent/whatsapp/contact/Header';
import Form from '@/components/agent/whatsapp/contact/Form';
import { WHATSAPP_LOCALSTORAGE_EVENTS } from '@/globals/agent/whatsapp';
import { HTTP_STATUS } from '@/globals';
import { mapActions } from 'vuex';
export default {
    inject: ['$helpers'],
    components: {
        Header,
        Form
    },
    methods: {
        ...mapActions([
            'agtWhatsContactDBFieldsInit',
            'agtWhatsSetCoversationInfo'
        ]),
        closeEvent () {
            this.$refs.formRef.clearForm();
        },
        async updatedLocalStorage () {
            this.conversationInfo =
        JSON.parse(localStorage.getItem('agtWhatsCoversationInfo')) || null;
            if (this.conversationInfo && this.conversationInfo?.client) {
                this.formToCreate = !this.conversationInfo?.client?.id;
            } else {
                this.formToCreate = false;
            }
            this.agtWhatsSetCoversationInfo(this.conversationInfo);
            this.$helpers.openLoader(this.$t);
            const { status, message } = await this.agtWhatsContactDBFieldsInit({
                campaignId: this.conversationInfo?.campaignId || null,
                conversationId: this.conversationInfo?.id || null
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
    },
    data () {
        return {
            conversationInfo: null,
            formToCreate: true
        };
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
