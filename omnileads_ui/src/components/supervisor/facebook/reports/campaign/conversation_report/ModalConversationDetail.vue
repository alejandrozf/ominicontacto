<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '70vw' }"
    :closable="false"
    :modal="false"
    :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
  >
    <ConversationDetail />
    <template #footer>
      <Button :label="$t('globals.close')" icon="pi pi-check" @click="closeModal" autofocus />
    </template>
  </Dialog>
</template>

<script>
import ConversationDetail from '@/components/supervisor/facebook/reports/campaign/conversation_report/ConversationDetail';

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
        closeModal () {
            this.$emit('handleModalEvent', {});
        }
    }
};
</script>
