<template>
  <Toolbar class="mb-4" :style="{ border: `4px solid ${whatsapp_color}` }">
    <template #start>
      <i
        class="pi pi-whatsapp mr-2"
        :style="{ color: whatsapp_color, 'font-size': '3rem' }"
      ></i>
      <h2 class="font-bold">{{ $t("globals.whatsapp.title") }}</h2>
    </template>
    <template #end>
      <Button
        icon="pi pi-plus"
        class="p-button-success"
        @click="newConversation"
        v-tooltip.top="$t('models.whatsapp.conversation.new.title')"
      />
      <Button
        icon="pi pi-times"
        class="p-button-danger ml-2"
        @click="close"
        v-tooltip.top="$t('globals.close')"
      />
    </template>
  </Toolbar>
</template>

<script>
import { COLORS } from '@/globals';
import { WHATSAPP_LOCALSTORAGE_EVENTS } from '@/globals/agent/whatsapp';
export default {
    inject: ['$helpers'],
    data () {
        return {
            whatsapp_color: COLORS.WHATSAPP.TealGreen
        };
    },
    methods: {
        newConversation () {
            if (this.$helpers.isSocketConnected(this.$t)) {
                localStorage.setItem('agtWhatsConversationNewResetForm', true);
                const modalEvent = new CustomEvent('onWhatsappConversationNewEvent', {
                    detail: {
                        conversation_new: true
                    }
                });
                window.parent.document.dispatchEvent(modalEvent);
                const event = new Event(
                    WHATSAPP_LOCALSTORAGE_EVENTS.CONVERSATION.NEW_INIT_DATA
                );
                window.parent.document.dispatchEvent(event);
            }
        },
        close () {
            const event = new CustomEvent('onWhatsappCloseContainerEvent', {
                detail: {
                    whatsapp_container: false
                }
            });
            window.parent.document.dispatchEvent(event);
        }
    }
};
</script>
