<template>
  <div>
    <div class="grid mb-2 mx-1" v-for="message in agtWhatsCoversationMessages" :key="message.id">
      <div class="col">
        <Message :message="message" />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import Message from '@/components/agent/whatsapp/conversation/Message';

export default {
    computed: {
        ...mapState(['agtWhatsCoversationMessages'])
    },
    components: {
        Message
    },
    watch: {
        agtWhatsCoversationMessages: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
