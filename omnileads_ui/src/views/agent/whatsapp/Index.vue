<template>
  <div>
    <HeaderMessages />
    <TabView>
      <TabPanel>
        <template #header>
          <span>{{ $t('views.whatsapp.conversations.answered')}}</span>
          <Badge :value="numAnsweredMessages" class="ml-2"></Badge>
        </template>
        <ListMessages :messages="answeredMessages" class="scroll"/>
      </TabPanel>
      <TabPanel>
        <template #header>
          <span>{{ $t('views.whatsapp.conversations.new')}}</span>
          <Badge :value="numNewMessages" class="ml-2"></Badge>
        </template>
        <ListMessages :messages="newMessages" class="scroll" />
      </TabPanel>
    </TabView>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import HeaderMessages from '@/components/agent/whatsapp/messages/HeaderMessages';
import ListMessages from '@/components/agent/whatsapp/messages/ListMessages';
import { WhatsappConsumer } from '@/services/agent/whatsapp/whatsapp_consumer';

export default {
    components: {
        HeaderMessages,
        ListMessages
    },
    computed: {
        ...mapState(['agtWhatsMessages'])
    },
    created () {
        this.consumer = new WhatsappConsumer();
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
        agtWhatsMessages: {
            handler () {
                this.newMessages = this.agtWhatsMessages.filter(
                    (m) => m.isNew === true
                );
                this.answeredMessages = this.agtWhatsMessages.filter(
                    (m) => m.isNew === false
                );
                this.numNewMessages = this.agtWhatsMessages.filter(
                    (m) => m.isNew === true && m.answered === false
                ).length;
                this.numAnsweredMessages = this.agtWhatsMessages.filter(
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
