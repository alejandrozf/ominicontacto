<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.whatsapp.line.edit_title") }}</h1>
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
    <FormSteps :formToEdit="true" :steps="steps" />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import FormSteps from '@/components/supervisor/whatsapp/lines/FormSteps';

export default {
    components: {
        FormSteps
    },
    data () {
        return {
            steps: []
        };
    },
    async created () {
        const id = this.$route.params.id;
        await this.initWhatsappLine({ id });
        await this.initGroupOfHours();
        await this.initWhatsappLineCampaigns();
        await this.initWhatsappProviders();
        await this.initWhatsappMessageTemplates();
        await this.initFormFlag();
        this.steps = [
            {
                label: this.$t('views.whatsapp.line.step1.title'),
                to: `/supervisor_whatsapp_lines/${id}/edit/step1`
            },
            {
                label: this.$t('views.whatsapp.line.step2.title'),
                to: `/supervisor_whatsapp_lines/${id}/edit/step2`
            },
            {
                label: this.$t('views.whatsapp.line.step3.title'),
                to: `/supervisor_whatsapp_lines/${id}/edit/step3`
            }
        ];
    },
    methods: {
        ...mapActions(['initGroupOfHours', 'initWhatsappLine', 'initFormFlag', 'initWhatsappLineCampaigns', 'initWhatsappProviders', 'initWhatsappMessageTemplates']),
        back () {
            this.$router.push({ name: 'supervisor_whatsapp_lines' });
        }
    }
};
</script>
