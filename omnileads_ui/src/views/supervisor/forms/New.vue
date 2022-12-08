<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("globals.new") }} {{ $tc("globals.form") }}</h1>
      </template>
      <template #end>
        <Button
          :label="$tc('globals.back')"
          icon="pi pi-arrow-left"
          class="p-button-info mr-2"
          @click="backToFormsList"
        />
      </template>
    </Toolbar>
    <FormSteps :steps="steps" />
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import FormSteps from '@/components/supervisor/forms/FormSteps';

export default {
    components: {
        FormSteps
    },
    data () {
        return {
            steps: [
                {
                    label: this.$t('views.form.step1.title'),
                    to: '/supervisor_forms/new/step1'
                },
                {
                    label: this.$t('views.form.step2.title'),
                    to: '/supervisor_forms/new/step2'
                },
                {
                    label: this.$t('views.form.step3.title'),
                    to: '/supervisor_forms/new/step3'
                }
            ]
        };
    },
    async created () {
        await this.initForms();
        this.initNewForm();
        this.initFormToCreateFlag(true);
    },
    methods: {
        ...mapActions(['initNewForm', 'initFormToCreateFlag', 'initForms']),
        backToFormsList () {
            this.$router.push({ name: 'supervisor_forms' });
        }
    }
};
</script>
