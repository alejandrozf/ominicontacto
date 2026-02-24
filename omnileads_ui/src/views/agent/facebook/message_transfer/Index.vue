<template>
  <div>
    <Header @handleCloseEvent="closeEvent" />
    <Form ref="formRef" />
  </div>
</template>

<script>
import Header from '@/components/agent/facebook/message_transfer/Header';
import Form from '@/components/agent/facebook/message_transfer/Form';
import { FACEBOOK_LOCALSTORAGE_EVENTS } from '@/globals/agent/facebook';
import { mapActions } from 'vuex';
export default {
    components: {
        Header,
        Form
    },
    methods: {
        ...mapActions([
            'agtFacebookTransferChatInitData',
            'agtFacebookSetConversationInfo'
        ]),
        closeEvent () {
            this.$refs.formRef.clearData();
        },
        async updatedLocalStorage (event) {
            const conversationInfo =
        JSON.parse(localStorage.getItem('agtFacebookConversationInfo')) || null;
            await this.agtFacebookSetConversationInfo(conversationInfo);
            await this.agtFacebookTransferChatInitData({
                campaingId: conversationInfo?.campaignId || null
            });
        }
    },
    mounted () {
        window.parent.document.addEventListener(
            FACEBOOK_LOCALSTORAGE_EVENTS.TRANSFER.FORM_INIT_DATA,
            this.updatedLocalStorage
        );
    },
    beforeUnmount () {
        window.parent.document.removeEventListener(
            FACEBOOK_LOCALSTORAGE_EVENTS.DISPOSITION.FORM_INIT_DATA,
            this.updatedLocalStorage
        );
    },
    async created () {
        await this.updatedLocalStorage();
    }
};
</script>
