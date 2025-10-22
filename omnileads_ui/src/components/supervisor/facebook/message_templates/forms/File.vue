<template>
  <div class="card">
    <div class="grid formgrid">
      <div class="field col-6">
        <label
          :class="{
            'p-error': v$.form.filename.$invalid && submitted,
          }"
          >{{ $t("forms.whatsapp.message_template.fields.filename") }}*</label
        >
        <div class="p-inputgroup mt-1">
          <span class="p-inputgroup-addon">
            <i class="pi pi-file"></i>
          </span>
          <InputText
            :class="{
              'p-invalid': v$.form.filename.$invalid && submitted,
            }"
            v-model="v$.form.filename.$model"
          />
        </div>
        <small>{{
          $t("forms.whatsapp.message_template.help_text.file.filename")
        }}</small>
        <br />
        <small
          v-if="
            (v$.form.filename.$invalid && submitted) ||
            v$.form.filename.$pending.$response
          "
          class="p-error"
          >{{
            v$.form.filename.required.$message.replace(
              "Value",
              $t("forms.whatsapp.message_template.fields.filename")
            )
          }}</small
        >
      </div>
      <div class="field col-6">
        <label
          :class="{
            'p-error': v$.form.url.$invalid && submitted,
          }"
          >{{ $t("forms.whatsapp.message_template.fields.url") }}*</label
        >
        <div class="p-inputgroup mt-1">
          <span class="p-inputgroup-addon">
            <i class="pi pi-link"></i>
          </span>
          <InputText
            :class="{
              'p-invalid': v$.form.url.$invalid && submitted,
            }"
            v-model="v$.form.url.$model"
          />
        </div>
        <small>{{
          $t("forms.whatsapp.message_template.help_text.file.url")
        }}</small>
        <br />
        <small
          v-if="
            (v$.form.url.$invalid && submitted) ||
            v$.form.url.$pending.$response
          "
          class="p-error"
          >{{
            v$.form.url.required.$message.replace(
              "Value",
              $t("forms.whatsapp.message_template.fields.url")
            )
          }}</small
        >
      </div>
    </div>
  </div>
</template>

<script>
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapState } from 'vuex';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                url: { required },
                filename: { required }
            }
        };
    },
    data () {
        return {
            form: {
                type: 'file',
                url: '',
                filename: ''
            },
            submitted: false
        };
    },
    created () {
        this.initializeData();
    },
    computed: {
        ...mapState(['supWhatsappMessageTemplateFormFields'])
    },
    methods: {
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        initFormData () {
            if (this.supWhatsappMessageTemplateFormFields) {
                this.form = {
                    type: 'file',
                    url: this.supWhatsappMessageTemplateFormFields.url,
                    filename: this.supWhatsappMessageTemplateFormFields.filename
                };
            }
        },
        save (isFormValid = !this.v$.$invalid) {
            this.submitted = true;
            if (!isFormValid) {
                return null;
            }
            this.submitted = false;
            return this.form;
        }
    },
    watch: {
        supWhatsappMessageTemplateFormFields: {
            handler () {
                this.initFormData();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
