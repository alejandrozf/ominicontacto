<template>
  <TabView class="tabview-custom">
    <TabPanel>
      <template #header>
        <i class="pi pi-list mr-2"></i>
        <span>{{ $t('views.whatsapp.disposition_form.form') }}</span>
      </template>
      <Form ref="formRef" @clearForm="clearFormEvent"/>
    </TabPanel>
    <TabPanel>
      <template #header>
        <i class="pi pi-history mr-2"></i>
        <span>{{ $t('views.whatsapp.disposition_form.record') }}</span>
      </template>
      <Historial ref="historialRef" />
    </TabPanel>
  </TabView>
</template>

<script>
import Form from '@/components/agent/whatsapp/disposition_chat/Form';
import Historial from '@/components/agent/whatsapp/disposition_chat/Historial';
export default {
    components: {
        Form,
        Historial
    },
    methods: {
        closeEvent () {
            this.$refs.formRef.resetData();
            this.$refs.historialRef.clearFilter();
        },
        clearFormEvent () {
            this.$refs.historialRef.clearFilter();
        }
    }
};
</script>
