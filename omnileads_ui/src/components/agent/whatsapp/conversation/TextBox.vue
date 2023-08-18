<template>
  <div class="grid mr-2">
    <div class="xl:col-11 lg:col-10 md:col-8 sm:col-9">
      <InputText
        class="w-full"
        autofocus
        :placeholder="$t('forms.form.enter_name')"
        @keyup.enter="sendMessage(message)"
        v-model="message"
      />
    </div>
    <div class="xl:col-1 lg:col-2 md:col-4 sm:col-3">
      <Button
        icon="pi pi-send"
        class="w-full"
        :disabled="message === ''"
        @click="sendMessage(message)"
        v-tooltip.top="$t('globals.send')"
      />
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import { WHATSAPP_MESSAGE } from '@/globals/agent/whatsapp';

export default {
    data () {
        return {
            message: ''
        };
    },
    methods: {
        ...mapActions(['agtWhatsCoversationSendTextMessage']),
        sendMessage () {
            if (this.message !== '') {
                this.$emit('scrollDownEvent');
                const data = {
                    message: {
                        id: 6,
                        from: 'Agente Sofia',
                        itsMine: true,
                        message: this.message,
                        sender: WHATSAPP_MESSAGE?.SENDERS?.AGENT,
                        status: WHATSAPP_MESSAGE?.STATUS?.SENT,
                        date: new Date()
                    },
                    conversationId: 1
                };
                this.agtWhatsCoversationSendTextMessage(data);
                this.message = '';
            }
        }
    }
};
</script>
