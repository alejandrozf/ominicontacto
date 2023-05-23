<template>
  <div>
    <Header @handleCloseEvent="closeEvent" />
    <Form ref="formRef" />
  </div>
</template>

<script>
import Header from '@/components/agent/whatsapp/message_transfer/Header';
import Form from '@/components/agent/whatsapp/message_transfer/Form';
import { mapActions } from 'vuex';
export default {
    components: {
        Header,
        Form
    },
    methods: {
        ...mapActions(['agtWhatsTransferChatInitData']),
        closeEvent () {
            this.$refs.formRef.clearData();
        }
    },
    async created () {
        await this.agtWhatsTransferChatInitData(1);
    }
};
</script>
