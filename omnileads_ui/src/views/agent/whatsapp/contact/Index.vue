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
    <SearchTable
      v-if="inconmingConversation"
      @selectPreviewContactEvent="selectPreviewContact"
      ref="searchTableRef"
      :conversationInfo="{ campaignId: conversationInfo?.campaignId }"
    />
    <Form
      ref="formRef"
      @cleanFilterSearchEvent="cleanFilterSearch"
      :formToCreate="formToCreate"
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
            formToCreate: true,
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
            this.$refs.searchTableRef.clearFilter();
        },
        selectPreviewContact (contact) {
            this.previewContact = contact;
        },
        closeEvent () {
            this.$refs.formRef.clearForm();
        },
        async updatedLocalStorage () {
            this.inconmingConversation =
        localStorage.getItem('agtWhatsInconmingConversation') === 'true';
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
