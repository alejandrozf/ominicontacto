<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("views.whatsapp.line.new_title") }}</h1>
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
    <FormSteps :steps="steps" />
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
            steps: [
                {
                    label: this.$t('views.whatsapp.line.step1.title'),
                    to: '/supervisor_whatsapp_lines/new/step1'
                },
                {
                    label: this.$t('views.whatsapp.line.step2.title'),
                    to: '/supervisor_whatsapp_lines/new/step2'
                },
                {
                    label: this.$t('views.whatsapp.line.step3.title'),
                    to: '/supervisor_whatsapp_lines/new/step3'
                }
            ]
        };
    },
    async created () {
        await this.initWhatsappProviders();
        await this.initWhatsappMessageTemplates();
        await this.initGroupOfHours();
        await this.initWhatsappLine({});
        await this.initWhatsappLineCampaigns();
        await this.initFormFlag(true);
    },
    methods: {
        ...mapActions(['initWhatsappLine', 'initWhatsappProviders', 'initGroupOfHours', 'initFormFlag', 'initWhatsappMessageTemplates', 'initWhatsappLineCampaigns']),
        back () {
            this.$router.push({ name: 'supervisor_whatsapp_lines' });
        }
    }
};
</script>
