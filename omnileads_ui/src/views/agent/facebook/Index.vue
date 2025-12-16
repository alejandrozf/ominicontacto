<template>
  <div>
    <HeaderMessages />
    <TabView>
      <TabPanel>
        <template #header>
          <span>{{ $t("views.whatsapp.conversations.answered") }}</span>
          <Badge :value="numAnsweredMessages.toString()" class="ml-2"></Badge>
        </template>
        <ListMessages :messages="answeredMessages" class="scroll" />
      </TabPanel>
      <TabPanel>
        <template #header>
          <span>{{ $t("views.whatsapp.conversations.new") }}</span>
          <Badge :value="numNewMessages.toString()" class="ml-2"></Badge>
        </template>
        <ListMessages :messages="newMessages" class="scroll" />
      </TabPanel>
    </TabView>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import HeaderMessages from '@/components/agent/facebook/messages/HeaderMessages';
import ListMessages from '@/components/agent/facebook/messages/ListMessages';
import { FacebookConsumer } from '@/web_sockets/facebook_consumer';

export default {
    components: {
        HeaderMessages,
        ListMessages
    },
    computed: {
        ...mapState(['agtFacebookChatsList'])
    },
    async created () {
        if (!this.consumer) {
            this.consumer = FacebookConsumer.getInstance({
                $t: this.$t
            });
        }
        console.log('RESET LOCALSTORAGE ON FACEBOOK INDEX');
        await this.agtFacebookChatsListInit();
        localStorage.setItem('agtFacebookConversationCreatedId', null);
        localStorage.setItem('agtFacebookConversationAttending', null);
        localStorage.setItem('agtFacebookConversationId', null);
        localStorage.setItem('agtFacebookConversationMessages', null);
        localStorage.setItem('agtFacebookMessageInfo', null);
        localStorage.setItem('onlyFacebookTemplates', null);
        localStorage.setItem('agtFacebookConversationNewResetForm', null);
        localStorage.setItem('agtFacebookConversationInfo', JSON.stringify(null));
    },
    mounted () {
        window.addEventListener('storage', this.updatedLocalStorage);
        this.updatedLocalStorage();
    },
    beforeUnmount () {
        window.removeEventListener('storage', this.updatedLocalStorage);
    },
    methods: {
        ...mapActions(['agtFacebookChatsListInit']),
        updatedLocalStorage () {
            const conversationId = localStorage.getItem('agtFacebookConversationCreatedId');
            if (conversationId !== 'null') {
                this.$router.push({
                    name: 'agent_facebook_conversation_detail',
                    params: { id: parseInt(conversationId) }
                });
                localStorage.setItem('agtFacebookConversationCreatedId', null);
            }
        }
    },
    data () {
        return {
            consumer: null,
            newMessages: [],
            answeredMessages: [],
            numNewMessages: 0,
            numAnsweredMessages: 0
        };
    },
    watch: {
        agtFacebookChatsList: {
            handler () {
                this.newMessages = this.agtFacebookChatsList.filter(
                    (m) => m.isNew === true
                );
                this.answeredMessages = this.agtFacebookChatsList.filter(
                    (m) => m.isNew === false
                );
                this.numNewMessages = this.agtFacebookChatsList.filter(
                    (m) => m.isNew === true && m.answered === false
                ).length;
                this.numAnsweredMessages = this.agtFacebookChatsList.filter(
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
