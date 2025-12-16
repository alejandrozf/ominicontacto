<template>
  <div @scrollend="onScroll" ref="scrollContainer">
    <div class="grid mb-2 mx-1" v-for="message in agtFacebookConversationMessages" :key="message.id">
      <div class="col">
        <Message :message="message" />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import Message from '@/components/agent/facebook/conversation/Message';

export default {
    computed: {
        ...mapState(['agtFacebookConversationMessages']),
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
      agtFacebookConversationMessages: {
            handler(newMsgs, oldMsgs) {
                console.log('agtFacebookConversationMessages changed:', newMsgs);

                // Filtramos mensajes no leídos
                var notReadMessageIds = newMsgs
                    .filter(msg => msg.status !== "read")
                    .map(msg => msg.id);

                if (this.autoScroll && this.$refs.scrollContainer) {
                    // Debounce del scroll para no saturar el hilo
                    if (this.scrollTimeout) clearTimeout(this.scrollTimeout);

                    this.scrollTimeout = setTimeout(() => {
                        this.$refs.scrollContainer.scroll({
                            top: this.$refs.scrollContainer.scrollHeight,
                            behavior: 'smooth'
                        });

                        if (notReadMessageIds.length) {
                            this.markItAsRead(notReadMessageIds);
                        }

                        this.scrollTimeout = null;
                    }, 50);
                }
            },
            deep: true,
            immediate: true
          }
    }

}
</script>
