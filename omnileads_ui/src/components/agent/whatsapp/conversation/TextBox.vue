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

export default {
    data () {
        return {
            message: ''
        };
    },
    methods: {
        ...mapActions(['agtWhatsCoversationSendMessage']),
        sendMessage () {
            if (this.message !== '') {
                this.$emit('scrollDownEvent');
                this.agtWhatsCoversationSendMessage({
                    id: 0,
                    from: 'Agent',
                    itsMine: true,
                    message: this.message,
                    date: new Date()
                });
                this.message = '';
            }
        }
    }
};
</script>
