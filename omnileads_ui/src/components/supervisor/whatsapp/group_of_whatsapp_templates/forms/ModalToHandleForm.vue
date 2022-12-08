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
          $t("views.whatsapp.whatsapp_template.new_title")
        }}
      </h2>
    </template>
    <Form @closeModalEvent="closeModal" />
  </Dialog>
</template>

<script>
import Form from '@/components/supervisor/whatsapp/group_of_whatsapp_templates/forms/Form';

export default {
    props: {
        showModal: {
            type: Boolean,
            default: false
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
