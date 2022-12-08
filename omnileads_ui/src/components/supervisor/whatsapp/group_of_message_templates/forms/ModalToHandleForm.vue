<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '25vw' }"
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
    <Form @closeModalEvent="closeModal" />
  </Dialog>
</template>

<script>
import Form from '@/components/supervisor/whatsapp/group_of_message_templates/forms/Form';

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
        closeModal () {
            this.$emit('handleModalEvent', {});
        }
    }
};
</script>
