<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.whatsapp.line", 2) }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.new')"
          icon="pi pi-plus"
          @click="newLine"
        />
      </template>
    </Toolbar>
    <LinesTable @handleModalEvent="handleModal" />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import LinesTable from '@/components/supervisor/whatsapp/lines/LinesTable';

export default {
    data () {
        return {
            showModal: false,
            formToCreate: false
        };
    },
    components: {
        LinesTable
    },
    async created () {
        await this.initWhatsappLines();
        await this.initWhatsappProviders();
    },
    methods: {
        handleModal ({ showModal = false, formToCreate = false, line = null }) {
            this.showModal = showModal;
            this.formToCreate = formToCreate;
            this.initWhatsappLine({ line });
        },
        newLine () {
            this.$router.push({ name: 'supervisor_whatsapp_lines_new_step1' });
        },
        ...mapActions(['initWhatsappLine', 'initWhatsappLines', 'initWhatsappProviders'])
    }
};
</script>
