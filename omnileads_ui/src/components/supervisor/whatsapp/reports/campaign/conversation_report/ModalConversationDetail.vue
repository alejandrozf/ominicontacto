<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '70vw' }"
    :closable="false"
    :modal="false"
  >
    <ConversationDetail />
    <template #footer>
        <Button :label="$t('globals.close')" icon="pi pi-check"  @click="closeModal" autofocus />
    </template>
  </Dialog>
</template>

<script>
import { mapActions } from 'vuex';
import ConversationDetail from '@/components/supervisor/whatsapp/reports/campaign/conversation_report/ConversationDetail';

export default {
    props: {
        showModal: {
            type: Boolean,
            default: false
        }
    },
    components: {
        ConversationDetail
    },
    methods: {
        ...mapActions(['']),
        closeModal () {
            this.$emit('handleModalEvent', {});
        }
    }
};
</script>
