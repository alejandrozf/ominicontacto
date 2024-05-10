<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.whatsapp.group_of_message_template.edit_title") }}</h1>
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
    <Form :formToCreate="false" />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import Form from '@/components/supervisor/whatsapp/group_of_message_templates/Form';

export default {
    components: {
        Form
    },
    async created () {
        const id = this.$route.params.id;
        await this.initWhatsappGroupOfMessageTemplate({ id });
        await this.initWhatsappMessageTemplates();
    },
    methods: {
        ...mapActions([
            'initWhatsappGroupOfMessageTemplate',
            'initWhatsappMessageTemplates'
        ]),
        back () {
            this.$router.push({
                name: 'supervisor_whatsapp_group_of_message_templates'
            });
        }
    }
};
</script>
