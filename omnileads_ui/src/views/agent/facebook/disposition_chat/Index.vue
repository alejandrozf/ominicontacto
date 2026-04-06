<template>
  <div>
    <Header @handleCloseEvent="closeEvent" />
    <Tab ref="tabRef" />
  </div>
</template>

<script>
import Header from '@/components/agent/facebook/disposition_chat/Header';
import Tab from '@/components/agent/facebook/disposition_chat/Tab';
import { mapActions } from 'vuex';
import { FACEBOOK_LOCALSTORAGE_EVENTS } from '@/globals/agent/facebook';
export default {
    components: {
        Header,
        Tab
    },
    methods: {
        ...mapActions([
            'agtFacebookDispositionChatHistoryInit',
            'agtFacebookDispositionChatOptionsInit',
            'agtFacebookSetConversationInfo',
            'agtFacebookDispositionChatSetFormFlag',
            'agtFacebookDispositionChatDetailInit'
        ]),
        closeEvent () {
            this.$refs.tabRef.closeEvent();
        },
        async updatedLocalStorage (event) {
            const conversationInfo =
        JSON.parse(localStorage.getItem('agtFacebookConversationInfo')) || null;
            const dispositionId = conversationInfo?.isDisposition
                ? conversationInfo?.client?.dispositionId || null
                : null;
            await this.agtFacebookSetConversationInfo(conversationInfo);
            await this.agtFacebookDispositionChatDetailInit({
                id: dispositionId
            });
            await this.agtFacebookDispositionChatOptionsInit({
                campaignId: conversationInfo?.campaignId || null
            });
            await this.agtFacebookDispositionChatHistoryInit({
                id: dispositionId
            });
            await this.agtFacebookDispositionChatSetFormFlag(!conversationInfo?.isDisposition);
        },
        async updateFlag () {
            const formToCreate =
        localStorage.getItem('agtFacebookDispositionChatFormToCreate') === 'true';
            await this.agtFacebookDispositionChatSetFormFlag(formToCreate);
        }
    },
    mounted () {
        window.parent.document.addEventListener(
            FACEBOOK_LOCALSTORAGE_EVENTS.DISPOSITION.FORM_INIT_DATA,
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
