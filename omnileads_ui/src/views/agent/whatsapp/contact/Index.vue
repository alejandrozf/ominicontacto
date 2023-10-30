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
import { mapActions } from 'vuex';
export default {
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
        updatedLocalStorage () {
            this.conversationInfo =
        JSON.parse(localStorage.getItem('agtWhatsCoversationInfo')) || null;
            this.formToCreate = !this.conversationInfo.client.id;
            this.agtWhatsSetCoversationInfo(this.conversationInfo);
        }
    },
    data () {
        return {
            conversationInfo: null,
            formToCreate: true
        };
    },
    mounted () {
        window.addEventListener('storage', this.updatedLocalStorage);
        this.updatedLocalStorage();
    },
    beforeUnmount () {
        window.removeEventListener('storage', this.updatedLocalStorage);
    },
    async created () {
        await this.updatedLocalStorage();
        await this.agtWhatsContactDBFieldsInit({
            campaignId: this.conversationInfo.campaignId,
            conversationId: this.conversationInfo.id
        });
    }
};
</script>
