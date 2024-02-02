<template>
  <div>
    <Header @handleCloseEvent="closeEvent" />
    <Form ref="formRef" />
  </div>
</template>

<script>
import Header from '@/components/agent/whatsapp/message_transfer/Header';
import Form from '@/components/agent/whatsapp/message_transfer/Form';
import { WHATSAPP_LOCALSTORAGE_EVENTS } from '@/globals/agent/whatsapp';
import { mapActions } from 'vuex';
export default {
    components: {
        Header,
        Form
    },
    methods: {
        ...mapActions([
            'agtWhatsTransferChatInitData',
            'agtWhatsSetCoversationInfo'
        ]),
        closeEvent () {
            this.$refs.formRef.clearData();
        },
        async updatedLocalStorage (event) {
            const conversationInfo =
        JSON.parse(localStorage.getItem('agtWhatsCoversationInfo')) || null;
            await this.agtWhatsSetCoversationInfo(conversationInfo);
            await this.agtWhatsTransferChatInitData({
                campaingId: conversationInfo?.campaignId || null
            });
        }
    },
    mounted () {
        window.parent.document.addEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.TRANSFER.FORM_INIT_DATA,
            this.updatedLocalStorage
        );
    },
    beforeUnmount () {
        window.parent.document.removeEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.DISPOSITION.FORM_INIT_DATA,
            this.updatedLocalStorage
        );
    },
    async created () {
        await this.updatedLocalStorage();
    }
};
</script>
