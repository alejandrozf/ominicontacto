<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h1>{{ $t("globals.edit") }} {{ $tc("globals.form") }}</h1>
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
    <FormSteps :formDetail="formDetail" :formToEdit="true" :steps="steps" />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import FormSteps from '@/components/supervisor/forms/FormSteps';

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
        await this.initForms();
        await this.initFormDetail(id);
        await this.initNewForm(this.formDetail);
        await this.initFormToCreateFlag(false);
        this.steps = [
            {
                label: this.$t('views.form.step1.title'),
                to: `/supervisor_forms/${this.formDetail.id}/edit/step1`
            },
            {
                label: this.$t('views.form.step2.title'),
                to: `/supervisor_forms/${this.formDetail.id}/edit/step2`
            },
            {
                label: this.$t('views.form.step3.title'),
                to: `/supervisor_forms/${this.formDetail.id}/edit/step3`
            }
        ];
    },
    methods: {
        ...mapActions(['initFormDetail', 'initNewForm', 'initFormToCreateFlag', 'initForms']),
        backToFormsList () {
            this.$router.push({ name: 'supervisor_forms' });
        }
    },
    computed: {
        ...mapState(['formDetail'])
    }
};
</script>
