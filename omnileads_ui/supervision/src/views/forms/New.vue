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
import FormSteps from '@/components/forms/FormSteps';

export default {
    components: {
        FormSteps
    },
    data () {
        return {
            steps: [
                {
                    label: this.$t('views.form.step1.title'),
                    to: '/forms/new/step1'
                },
                {
                    label: this.$t('views.form.step2.title'),
                    to: '/forms/new/step2'
                },
                {
                    label: this.$t('views.form.step3.title'),
                    to: '/forms/new/step3'
                }
            ]
        };
    },
    created () {
        this.initNewForm();
        this.initFormToCreateFlag(true);
    },
    methods: {
        ...mapActions(['initNewForm', 'initFormToCreateFlag']),
        backToFormsList () {
            this.$router.push({ name: 'forms' });
        }
    }
};
</script>
