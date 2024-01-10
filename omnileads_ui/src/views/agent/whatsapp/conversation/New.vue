<template>
  <div>
    <h2>
      {{ $t("models.whatsapp.conversation.new.title") }}
    </h2>
    <Form @closeModalEvent="closeModal" />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import Form from '@/components/agent/whatsapp/conversation/new/Form';
import { WHATSAPP_LOCALSTORAGE_EVENTS } from '@/globals/agent/whatsapp';
import { HTTP_STATUS } from '@/globals';

export default {
    inject: ['$helpers'],
    components: {
        Form
    },
    async created () {
        await this.updatedLocalStorage();
    },
    async mounted () {
        window.parent.document.addEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.CONVERSATION.NEW_INIT_DATA,
            this.updatedLocalStorage
        );
    },
    beforeUnmount () {
        window.parent.document.removeEventListener(
            WHATSAPP_LOCALSTORAGE_EVENTS.CONVERSATION.NEW_INIT_DATA,
            this.updatedLocalStorage
        );
    },
    methods: {
        ...mapActions(['initWhatsappLineCampaigns']),
        async updatedLocalStorage () {
            this.$helpers.openLoader(this.$t);
            setTimeout(async () => {
                const { status, message } = await this.initWhatsappLineCampaigns();
                this.$helpers.closeLoader();
                if (status !== HTTP_STATUS.SUCCESS) {
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.error_notification'),
                            message,
                            this.$t('globals.icon_error')
                        )
                    );
                }
            }, 2000);
        },
        closeModal () {
            const event = new CustomEvent('onWhatsappConversationNewEvent', {
                detail: {
                    conversation_new: false
                }
            });
            window.parent.document.dispatchEvent(event);
        }
    }
};
</script>
