<template>
  <div>
    <Header @handleCloseEvent="closeEvent" />
    <Tab ref="tabRef" />
  </div>
</template>

<script>
import Header from '@/components/agent/whatsapp/disposition_chat/Header';
import Tab from '@/components/agent/whatsapp/disposition_chat/Tab';
import { mapActions } from 'vuex';
import { WHATSAPP_LOCALSTORAGE_EVENTS } from '@/globals/agent/whatsapp';
export default {
    components: {
        Header,
        Tab
    },
    methods: {
        ...mapActions([
            'agtWhatsDispositionChatHistoryInit',
            'agtWhatsDispositionChatOptionsInit',
            'agtWhatsSetCoversationInfo',
            'agtWhatsDispositionChatSetFormFlag',
            'agtWhatsDispositionChatDetailInit'
        ]),
        closeEvent () {
            this.$refs.tabRef.closeEvent();
        },
        async updatedLocalStorage (event) {
            const conversationInfo =
        JSON.parse(localStorage.getItem('agtWhatsCoversationInfo')) || null;
            await this.agtWhatsSetCoversationInfo(conversationInfo);
            await this.agtWhatsDispositionChatDetailInit({
                id: conversationInfo?.client?.dispositionId || null
            });
            await this.agtWhatsDispositionChatOptionsInit({
                campaignId: conversationInfo?.campaignId || null
            });
            await this.agtWhatsDispositionChatHistoryInit({
                id: conversationInfo?.client?.dispositionId || null
            });
            await this.agtWhatsDispositionChatSetFormFlag(conversationInfo?.client?.dispositionId === null);
        },
        async updateFlag () {
            const formToCreate =
        localStorage.getItem('agtWhatsDispositionChatFormToCreate') === 'true';
            await this.agtWhatsDispositionChatSetFormFlag(formToCreate);
        }
    },
    mounted () {
        window.parent.document.addEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.DISPOSITION.FORM_INIT_DATA,
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
