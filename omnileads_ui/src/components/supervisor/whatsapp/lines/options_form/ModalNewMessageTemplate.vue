<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '60vw' }"
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
    <Form
      @closeModalEvent="closeModal"
      :formToCreate="formToCreate"
      :return_after_save=return_after_save
    />
  </Dialog>
</template>

<script>
import { mapActions } from 'vuex';
import Form from '@/components/supervisor/whatsapp/message_templates/Form';
import { WHATSAPP_URL_NAME } from '@/globals/supervisor/whatsapp';

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
        Form,
        WHATSAPP_URL_NAME
    },
    computed: {
      return_after_save() {
        return `${WHATSAPP_URL_NAME}_lines_new_step3`
      }
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
