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
import { HTTP_STATUS } from '@/globals';
import { mapActions, mapState } from 'vuex';

export default {
    inject: ['$helpers'],
    props: {
        conversationId: {
            type: Number,
            required: true,
            default: null
        }
    },
    data () {
        return {
            message: ''
        };
    },
    computed: {
        ...mapState(['agtWhatsCoversationInfo'])
    },
    methods: {
        ...mapActions(['agtWhatsCoversationSendTextMessage']),
        async sendMessage () {
            if (this.$helpers.isSocketConnected(this.$t)) {
                if (this.message !== '') {
                    const data = {
                        message: {
                            message: this.message
                        },
                        conversationId: this.conversationId,
                        phoneLine: this.agtWhatsCoversationInfo.line.number,
                        $t: this.$t
                    };
                    this.message = '';
                    const { status, message } = await this.agtWhatsCoversationSendTextMessage(data);
                    if (status === HTTP_STATUS.SUCCESS) {
                        this.$emit('scrollDownEvent');
                    } else {
                        this.$swal(
                            this.$helpers.getToasConfig(
                                this.$t('globals.error_notification'),
                                message,
                                this.$t('globals.icon_error')
                            )
                        );
                    }
                }
            }
        }
    },
    watch: {
        conversationId: {
            handler () {},
            deep: true,
            immediate: true
        },
        agtWhatsCoversationInfo: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
