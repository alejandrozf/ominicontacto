<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '40vw' }"
    :closable="false"
    :modal="false"
  >
    <template #header>
      <h2>
        {{
          formToCreate
            ? $t("views.whatsapp.message_template.new_title")
            : $t("views.whatsapp.message_template.edit_title")
        }}
      </h2>
    </template>
    <Form @closeModalEvent="closeModal" :formToCreate="formToCreate" />
  </Dialog>
</template>

<script>
import { mapActions } from 'vuex';
import Form from '@/components/supervisor/whatsapp/message_templates/Form';

export default {
    props: {
        showModal: {
            type: Boolean,
            default: false
        },
        formToCreate: {
            type: Boolean,
            default: true
        }
    },
    components: {
        Form
    },
    methods: {
        ...mapActions(['initWhatsappMessageTemplate']),
        closeModal () {
            this.$emit('handleModalEvent', {});
            this.initWhatsappMessageTemplate({});
        }
    }
};
</script>
