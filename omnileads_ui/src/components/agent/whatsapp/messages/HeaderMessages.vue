<template>
  <Toolbar class="mb-4">
    <template #start>
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
export default {
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
