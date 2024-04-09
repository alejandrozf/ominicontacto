<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h2 class="font-bold">{{ title }}</h2>
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
    props: {
        title: {
            type: String,
            default: ''
        }
    },
    methods: {
        close () {
            this.$emit('handleCloseEvent');
            const event = new CustomEvent('onWhatsappContactFormEvent', {
                detail: {
                    contact_form: false
                }
            });
            window.parent.document.dispatchEvent(event);
        }
    }
};
</script>
