<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h2 class="font-bold">Respuestas rapidas</h2>
      </template>
      <template #end>
        <Button
          icon="pi pi-times"
          class="p-button-danger"
          @click="close()"
          v-tooltip.top="'Cerrar'"
        />
      </template>
    </Toolbar>
  </div>
</template>

<script>
export default {
    methods: {
        close () {
            this.$emit('handleClearFiltersEvent');
            const event = new CustomEvent('onWhatsappTemplatesEvent', {
                detail: {
                    templates: false,
                    conversationId: null
                }
            });
            window.parent.document.dispatchEvent(event);
        }
    }
};
</script>
