<template>
  <div class="card">
    <div class="fluid grid formgrid mt-4">
      <div class="field col-6">
        <label
          id="form_name"
          :class="{
            'p-error': v$.newForm.nombre.$invalid && submitted || repeatedFormName,
          }"
          >{{ $t("models.form.name") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="form_name"
            :class="{
              'p-invalid': v$.newForm.nombre.$invalid && submitted || repeatedFormName,
            }"
            @input="validateFormName"
            :placeholder="$t('forms.form.enter_name')"
            v-model="v$.newForm.nombre.$model"
          />
        </div>
        <small
          v-if="
            (v$.newForm.nombre.$invalid && submitted) ||
            v$.newForm.nombre.$pending.$response
          "
          class="p-error"
          >{{
            v$.newForm.nombre.required.$message.replace(
              "Value",
              $t("models.form.name")
            )
          }}</small
        >
        <small
          v-if="
            repeatedFormName
          "
          class="p-error"
          >{{
            $t('forms.form.validations.repeated_form_name')
          }}</small
        >
      </div>
      <div class="field col-6">
        <label
          id="form_descripcion"
          :class="{
            'p-error': v$.newForm.descripcion.$invalid && submitted,
          }"
          >{{ $t("models.form.description") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-align-left"></i>
          </span>
          <Textarea
            rows="10"
            cols="30"
            id="form_descripcion"
            :class="{
              'p-invalid': v$.newForm.descripcion.$invalid && submitted,
            }"
            :placeholder="$t('forms.form.enter_description')"
            v-model="v$.newForm.descripcion.$model"
          />
        </div>
        <small
          v-if="
            (v$.newForm.descripcion.$invalid && submitted) ||
            v$.newForm.descripcion.$pending.$response
          "
          class="p-error"
          >{{
            v$.newForm.descripcion.required.$message.replace(
              "Value",
              $t("models.form.description")
            )
          }}</small
        >
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap">
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.next')"
          icon="pi pi-angle-right"
          icon-pos="right"
          class="mt-4 p-button-secondary"
          @click="nextPage(!v$.$invalid)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            newForm: {
                nombre: { required },
                descripcion: { required }
            }
        };
    },
    inject: ['$helpers'],
    data () {
        return {
            submitted: false,
            repeatedFormName: false
        };
    },
    computed: {
        ...mapState(['newForm', 'forms'])
    },
    methods: {
        validateFormName () {
            this.repeatedFormName = this.forms.find(f => f.nombre === this.newForm.nombre) !== undefined;
        },
        nextPage (isFormValid) {
            this.submitted = true;
            if (isFormValid && !this.repeatedFormName) {
                this.$emit('next-page', { pageIndex: 0 });
            } else {
                return null;
            }
        }
    },
    watch: {
        forms: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
