<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.whatsapp.group_of_whatsapp_template", 2) }}</h1>
      </template>
      <template #end>
        <Button :label="$tc('globals.new')" icon="pi pi-plus" @click="create" />
      </template>
    </Toolbar>
    <GroupOfWhatsappTemplateTable />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import GroupOfWhatsappTemplateTable from '@/components/supervisor/whatsapp/group_of_whatsapp_templates/Table';

export default {
    components: {
        GroupOfWhatsappTemplateTable
    },
    async created () {
        await this.initWhatsappGroupOfWhatsappTemplates();
    },
    methods: {
        ...mapActions(['initWhatsappGroupOfWhatsappTemplates']),
        create () {
            this.$router.push({
                name: 'supervisor_whatsapp_group_of_whatsapp_templates_new'
            });
        }
    }
};
</script>
