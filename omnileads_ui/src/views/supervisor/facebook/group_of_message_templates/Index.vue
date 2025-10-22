<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $tc("globals.whatsapp.group_of_message_template", 2) }}</h1>
      </template>
      <template #end>
        <Button :label="$tc('globals.new')" icon="pi pi-plus" @click="create" />
      </template>
    </Toolbar>
    <GroupOfMessageTemplateTable />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import GroupOfMessageTemplateTable from '@/components/supervisor/whatsapp/group_of_message_templates/Table';

export default {
    components: {
        GroupOfMessageTemplateTable
    },
    async created () {
        await this.initWhatsappGroupOfMessageTemplates();
    },
    methods: {
        ...mapActions(['initWhatsappGroupOfMessageTemplates']),
        create () {
            this.$router.push({
                name: 'supervisor_whatsapp_group_of_message_templates_new'
            });
        }
    }
};
</script>
