<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h2 class="font-bold">{{ $t('views.whatsapp.disposition_form.management') }}</h2>
      </template>
      <template #end>
        <Button
          icon="pi pi-times"
          class="p-button-danger"
          @click="close()"
          v-tooltip.top="$t('globals.close')"
        />
      </template>
    </Toolbar>
  </div>
</template>

<script>
export default {
    methods: {
        close () {
            this.$emit('handleCloseEvent');
            const event = new CustomEvent('onWhatsappDispositionFormEvent', {
                detail: {
                    disposition_form: false
                }
            });
            window.parent.document.dispatchEvent(event);
        }
    }
};
</script>
