<template>
  <div class="grid">
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
        ...mapState(['agtFacebookConversationInfo'])
    },
    methods: {
        ...mapActions(['agtFacebookConversationSendTextMessage']),
        async sendMessage () {
            console.log('Sending message:', this.message);
            if (this.$helpers.isSocketConnected(this.$t) || true) {
                if (this.message !== '') {
                    const data = {
                        message: {
                            message: this.message
                        },
                        conversationId: this.conversationId,
                        pageId: this.agtFacebookConversationInfo.page.page_id,
                        $t: this.$t
                    };
                    this.message = '';
                    console.log('Prepared data for sending:', data);
                    const { status, message } = await this.agtFacebookConversationSendTextMessage(data);
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
        agtFacebookConversationInfo: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
