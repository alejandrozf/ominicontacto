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

export default {
    components: {
        Form
    },
    async created () {
        await this.initWhatsappLineCampaigns();
    },
    mounted () {
        window.addEventListener('storage', this.updatedLocalStorage);
        this.updatedLocalStorage();
    },
    beforeUnmount () {
        window.removeEventListener('storage', this.updatedLocalStorage);
    },
    methods: {
        ...mapActions(['initWhatsappLineCampaigns']),
        async updatedLocalStorage () {
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
