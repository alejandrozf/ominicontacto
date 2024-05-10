<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.whatsapp.provider", 2) }}</h1>
      </template>
    </Toolbar>
    <ProvidersTable @handleModalEvent="handleModal" />
    <ModalToHandleProvider
      :showModal="showModal"
      :formToCreate="formToCreate"
      @handleModalEvent="handleModal"
    />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import ProvidersTable from '@/components/supervisor/whatsapp/providers/ProvidersTable';
import ModalToHandleProvider from '@/components/supervisor/whatsapp/providers/ModalToHandleProvider';

export default {
    data () {
        return {
            showModal: false,
            formToCreate: false
        };
    },
    components: {
        ProvidersTable,
        ModalToHandleProvider
    },
    async created () {
        await this.initWhatsappProviders();
    },
    methods: {
        handleModal ({ showModal = false, formToCreate = false, provider = null }) {
            this.showModal = showModal;
            this.formToCreate = formToCreate;
            this.initWhatsappProvider({ provider });
        },
        ...mapActions(['initWhatsappProviders', 'initWhatsappProvider'])
    }
};
</script>
