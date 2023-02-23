<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.whatsapp.whatsapp_template", 2) }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="back"
        />
      </template>
    </Toolbar>
    <WhatsappTemplatesTable />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import WhatsappTemplatesTable from '@/components/supervisor/whatsapp/whatsapp_templates/WhatsappTemplatesTable';

export default {
    components: {
        WhatsappTemplatesTable
    },
    async created () {
        const id = this.$route.params.id;
        await this.sycnupWhatsappTemplates(id);
        await this.initSupWhatsappTemplates();
    },
    methods: {
        ...mapActions([
            'initSupWhatsappTemplates',
            'sycnupWhatsappTemplates'
        ]),
        back () {
            this.$router.push({ name: 'supervisor_whatsapp_lines' });
        }
    }
};
</script>
