<template>
  <div class="card">
    <h3>{{ $t("views.form.step3.display_name") }} {{ newForm.nombre }}</h3>
    <h3>
      {{ $t("views.form.step3.display_description") }} {{ newForm.descripcion }}
    </h3>
    <div class="grid formgrid mt-4">
      <div
        v-for="campo in newForm.campos.sort((a, b) =>
          a.orden > b.orden ? 1 : -1
        )"
        :key="campo.id"
        class="field col-6 mt-4"
      >
        <label
          >{{ campo.nombre_campo }} {{ campo.is_required ? "*" : "" }}</label
        >
        <br />
        <InputText class="w-full mt-2" v-if="campo.tipo == 1" type="text" />
        <Calendar class="w-full mt-2" v-else-if="campo.tipo == 2" />
        <Dropdown class="w-full mt-2" v-else-if="campo.tipo == 3" :options="JSON.parse(campo.values_select)" />
        <InputNumber v-else-if="campo.tipo == 5 && campo.tipo_numero == 1" class="w-full mt-2"  :useGrouping="false" />
        <InputNumber v-else-if="campo.tipo == 5 && campo.tipo_numero == 2" class="w-full mt-2"  :useGrouping="false" :minFractionDigits="0" :maxFractionDigits="campo.cifras_significativas" />
        <Textarea class="w-full mt-2" v-else rows="5" cols="30" />
      </div>
    </div>
    <div class="flex justify-content-between flex-wrap mb-4">
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.back')"
          icon="pi pi-angle-left"
          icon-pos="right"
          class="p-button-secondary"
          @click="prevPage"
        />
      </div>
      <div class="flex align-items-center justify-content-center">
        <Button :label="$t('globals.save')" icon="pi pi-save" @click="save" />
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { HTTP_STATUS } from '@/globals';

export default {
    inject: ['$helpers'],
    data () {
        return {
            formErrors: []
        };
    },
    computed: {
        ...mapState(['newForm', 'isFormToCreate'])
    },
    methods: {
        ...mapActions(['createForm', 'updateForm']),
        prevPage () {
            this.$emit('prev-page', { pageIndex: 2 });
        },
        validateFormData () {
            this.formErrors = [];
            if (this.newForm.nombre === '') {
                this.formErrors.push(this.$t('forms.form.validations.required_name'));
            }
            if (this.newForm.descripcion === '') {
                this.formErrors.push(
                    this.$t('forms.form.validations.required_description')
                );
            }
            if (this.newForm.campos.length === 0) {
                this.formErrors.push(
                    this.$t('forms.form.validations.not_empty_form_field')
                );
            }
        },
        async save () {
            this.validateFormData();
            if (this.formErrors.length > 0) {
                var errors = '<ul>';
                this.formErrors.forEach((e) => {
                    errors += `<li>${e}<li/>`;
                });
                errors += '<ul/>';
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.warning_notification'),
                        null,
                        this.$t('globals.icon_warning'),
                        null,
                        errors
                    )
                );
                return null;
            }
            var response = null;
            if (this.isFormToCreate) {
                response = await this.createForm(this.newForm);
            } else {
                response = await this.updateForm({
                    id: this.newForm.id,
                    data: this.newForm
                });
            }
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                this.$router.push({ name: 'supervisor_forms' });
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        message,
                        this.$t('globals.icon_success')
                    )
                );
            } else {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        message,
                        this.$t('globals.icon_error')
                    )
                );
            }
        }
    }
};
</script>
