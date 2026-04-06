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
            ? $t("views.facebook.message_template.new_title")
            : $t("views.facebook.message_template.edit_title")
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
import Form from '@/components/supervisor/facebook/message_templates/Form';
import { FACEBOOK_URL_NAME } from '@/globals/supervisor/facebook';

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
        FACEBOOK_URL_NAME
    },
    computed: {
      return_after_save() {
        return `${FACEBOOK_URL_NAME}_pages_new_step3`
      }
    },
    methods: {
        ...mapActions(['initFacebookPageTemplate']),
        closeModal () {
            this.$emit('handleModalEvent', {});
            this.initFacebookPageTemplate({});
        }
    }
};
</script>
