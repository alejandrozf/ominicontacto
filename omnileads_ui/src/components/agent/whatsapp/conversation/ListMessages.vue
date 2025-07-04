<template>
  <div @scrollend="onScroll" ref="scrollContainer">
    <div class="grid mb-2 mx-1" v-for="message in agtWhatsCoversationMessages" :key="message.id">
      <div class="col">
        <Message :message="message" />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import Message from '@/components/agent/whatsapp/conversation/Message';

export default {
    computed: {
        ...mapState(['agtWhatsCoversationMessages']),
        ...mapActions([])
    },
    components: {
        Message
    },
    data() {
      return {
        autoScroll: true,
      }
    },
    methods: {
      ...mapActions(['markMessageAsRead']),
      onScroll({ target: { scrollTop, clientHeight, scrollHeight } }) {
        if (scrollTop + clientHeight >= scrollHeight - 200) {
          this.autoScroll = true
        } else {
          this.autoScroll = false
        }
      },
      async markItAsRead(notReadMessageIds){
        return await this.markMessageAsRead(notReadMessageIds);
      }
    },
    watch: {
        agtWhatsCoversationMessages: {
            handler (newMsgs, oldMsgs) {
              var notReadMessageIds = newMsgs.filter((msg)=> msg.status !== "read")
              notReadMessageIds = notReadMessageIds.map((msg) => msg.id)
              if (this.autoScroll && this.$refs.scrollContainer) {
                setTimeout(() => {
                  this.$refs.scrollContainer.scroll({
                    top: this.$refs.scrollContainer.scrollHeight,
                    behavior: 'smooth',
                  });
                }, 0);
                if (notReadMessageIds){
                  this.markItAsRead(notReadMessageIds);
                }
              }
            },
            deep: true,
            // immediate: true
        }
    }
};
</script>
