<template>
  <div>
    <HeaderMessages />
    <TabView>
      <TabPanel>
        <template #header>
          <span>{{ $t("views.whatsapp.conversations.answered") }}</span>
          <Badge :value="numAnsweredMessages" class="ml-2"></Badge>
        </template>
        <ListMessages :messages="answeredMessages" class="scroll" />
      </TabPanel>
      <TabPanel>
        <template #header>
          <span>{{ $t("views.whatsapp.conversations.new") }}</span>
          <Badge :value="numNewMessages" class="ml-2"></Badge>
        </template>
        <ListMessages :messages="newMessages" class="scroll" />
      </TabPanel>
    </TabView>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import HeaderMessages from '@/components/agent/whatsapp/messages/HeaderMessages';
import ListMessages from '@/components/agent/whatsapp/messages/ListMessages';
import { WhatsappConsumer } from '@/web_sockets/whatsapp_consumer';

export default {
    components: {
        HeaderMessages,
        ListMessages
    },
    computed: {
        ...mapState(['agtWhatsChatsList'])
    },
    async created () {
        if (!this.consumer) {
            this.consumer = new WhatsappConsumer();
        }
        await this.agtWhatsChatsListInit();
        localStorage.setItem('agtWhatsConversationCreatedId', null);
        localStorage.setItem('agtWhatsappConversationAttending', null);
        localStorage.setItem('agtWhatsappConversationId', null);
        localStorage.setItem('agtWhatsappConversationMessages', null);
        localStorage.setItem('agtWhatsMessageInfo', null);
        localStorage.setItem('onlyWhatsappTemplates', null);
        localStorage.setItem('agtWhatsConversationNewResetForm', null);
        localStorage.setItem('agtWhatsCoversationInfo', null);
    },
    mounted () {
        window.addEventListener('storage', this.updatedLocalStorage);
        this.updatedLocalStorage();
    },
    beforeUnmount () {
        window.removeEventListener('storage', this.updatedLocalStorage);
    },
    methods: {
        ...mapActions(['agtWhatsChatsListInit']),
        updatedLocalStorage () {
            const conversationId = localStorage.getItem('agtWhatsCoversationCreatedId');
            if (conversationId !== 'null') {
                this.$router.push({
                    name: 'agent_whatsapp_conversation_detail',
                    params: { id: parseInt(conversationId) }
                });
                localStorage.setItem('agtWhatsCoversationCreatedId', null);
            }
        }
    },
    data () {
        return {
            newMessages: [],
            answeredMessages: [],
            numNewMessages: 0,
            numAnsweredMessages: 0
        };
    },
    watch: {
        agtWhatsChatsList: {
            handler () {
                this.newMessages = this.agtWhatsChatsList.filter(
                    (m) => m.isNew === true
                );
                this.answeredMessages = this.agtWhatsChatsList.filter(
                    (m) => m.isNew === false
                );
                this.numNewMessages = this.agtWhatsChatsList.filter(
                    (m) => m.isNew === true && m.answered === false
                ).length;
                this.numAnsweredMessages = this.agtWhatsChatsList.filter(
                    (m) => m.isNew === false && m.answered === false
                ).length;
            },
            deep: true,
            immediate: true
        }
    }
};
</script>

<style scoped>
.scroll {
  overflow-y: scroll;
  height: calc(100vh - 250px);
}
</style>
