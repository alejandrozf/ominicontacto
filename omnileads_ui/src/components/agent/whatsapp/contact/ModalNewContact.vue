<template>
  <Dialog
    v-model:visible="showModal"
    :style="{ width: '70vw' }"
    :modal="false"
    :closable="false"
  >
    <template #header>
      <h2>
          {{ $t("models.whatsapp.conversation.new.model.contact") }}
      </h2>
    </template>
    <Form
      @closeModalEvent="closeModal"
      :formToCreateFromNewConversation="true"
      :formToCreate="false"
    />
  </Dialog>
</template>

<script>
import Form from '@/components/agent/whatsapp/contact/Form';
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
    computed:{

    },
    methods: {
        closeModal (response) {
            this.$emit('handleModalEvent', {showModal:false});
        },
    },
    watch: {
        showModal: {
            handler () {},
            deep: true,
            immediate: true
        }
    },
};
</script>
