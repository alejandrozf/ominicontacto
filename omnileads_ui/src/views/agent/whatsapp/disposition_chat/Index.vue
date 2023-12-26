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
    // async mounted () {
    //     console.log('===> mounted disposition chat');
    //     window.document.addEventListener(
    //         'agtWhatsCoversationInfo',
    //         this.updatedLocalStorage
    //     );
    //     window.document.addEventListener(
    //         'agtWhatsDispositionChatFormFlag',
    //         this.updateFlag
    //     );
    // },
    // beforeUnmount () {
    //     console.log('===> beforeUnmount disposition chat');
    //     window.addEventListener(
    //         'agtWhatsCoversationInfo',
    //         this.updatedLocalStorage
    //     );
    //     window.addEventListener('agtWhatsDispositionChatFormFlag', this.updateFlag);
    // },
    async created () {
        await this.updatedLocalStorage();
    // await this.agtWhatsDispositionChatHistoryInit({ id: this.conversationInfo.dispositionChatId });
    }
};
</script>
