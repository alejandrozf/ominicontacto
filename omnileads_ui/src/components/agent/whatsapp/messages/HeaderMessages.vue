<template>
  <Toolbar class="mb-4" :style="{border: `4px solid ${whatsapp_color}`}">
    <template #start>
      <i class="pi pi-whatsapp mr-2" :style="{ color: whatsapp_color, 'font-size': '3rem'}"></i>
      <h2 class="font-bold">{{ $t('globals.whatsapp.title') }}</h2>
    </template>
    <template #end>
      <!-- <Button
      icon="pi pi-comment"
      class="p-button-secondary"
      @click="newConversation"
      v-tooltip.top="'Nueva conversarion'"
      /> -->
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
export default {
    data () {
        return {
            whatsapp_color: COLORS.WHATSAPP.TealGreen
        };
    },
    methods: {
        newConversation () {
            const event = new CustomEvent('onWhatsappNewConversationEvent', {
                detail: {
                    new_conversation: false
                }
            });
            window.parent.document.dispatchEvent(event);
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
