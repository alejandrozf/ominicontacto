<template>
  <div class="card">
    <div class="grid formgrid">
      <div class="field col-6">
        <label
          :class="{
            'p-error': v$.form.originalUrl.$invalid && submitted,
          }"
          >{{ $t("forms.whatsapp.message_template.fields.url") }}*</label
        >
        <div class="p-inputgroup mt-1">
          <span class="p-inputgroup-addon">
            <i class="pi pi-link"></i>
          </span>
          <InputText
            :class="{
              'p-invalid': v$.form.originalUrl.$invalid && submitted,
            }"
            v-model="v$.form.originalUrl.$model"
          />
        </div>
        <small>{{
          $t("forms.whatsapp.message_template.help_text.image.original_url")
        }}</small>
        <br />
        <small
          v-if="
            (v$.form.originalUrl.$invalid && submitted) ||
            v$.form.originalUrl.$pending.$response
          "
          class="p-error"
          >{{
            v$.form.originalUrl.required.$message.replace(
              "Value",
              $t("forms.whatsapp.message_template.fields.url")
            )
          }}</small
        >
      </div>
      <div class="field col-6">
        <label
          :class="{
            'p-error': v$.form.previewUrl.$invalid && submitted,
          }"
          >{{
            $t("forms.whatsapp.message_template.fields.preview_url")
          }}*</label
        >
        <div class="p-inputgroup mt-1">
          <span class="p-inputgroup-addon">
            <i class="pi pi-link"></i>
          </span>
          <InputText
            :class="{
              'p-invalid': v$.form.previewUrl.$invalid && submitted,
            }"
            v-model="v$.form.previewUrl.$model"
          />
        </div>
        <small>{{
          $t("forms.whatsapp.message_template.help_text.image.preview_url")
        }}</small>
        <br />
        <small
          v-if="
            (v$.form.previewUrl.$invalid && submitted) ||
            v$.form.previewUrl.$pending.$response
          "
          class="p-error"
          >{{
            v$.form.previewUrl.required.$message.replace(
              "Value",
              $t("forms.whatsapp.message_template.fields.preview_url")
            )
          }}</small
        >
      </div>
    </div>
    <div class="grid formgrid">
      <div class="field col-6">
        <label
          :class="{
            'p-error': v$.form.caption.$invalid && submitted,
          }"
          >{{ $t("forms.whatsapp.message_template.fields.caption") }}*</label
        >
        <div class="p-inputgroup mt-1">
          <span class="p-inputgroup-addon">
            <i class="pi pi-info-circle"></i>
          </span>
          <InputText
            :class="{
              'p-invalid': v$.form.caption.$invalid && submitted,
            }"
            v-model="v$.form.caption.$model"
          />
        </div>
        <small>{{
          $t("forms.whatsapp.message_template.help_text.image.caption")
        }}</small>
        <br />
        <small
          v-if="
            (v$.form.caption.$invalid && submitted) ||
            v$.form.caption.$pending.$response
          "
          class="p-error"
          >{{
            v$.form.caption.required.$message.replace(
              "Value",
              $t("forms.whatsapp.message_template.fields.caption")
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
                originalUrl: { required },
                previewUrl: { required },
                caption: { required }
            }
        };
    },
    data () {
        return {
            form: {
                type: 'image',
                originalUrl: '',
                previewUrl: '',
                caption: ''
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
                    type: 'image',
                    originalUrl: this.supWhatsappMessageTemplateFormFields.originalUrl,
                    previewUrl: this.supWhatsappMessageTemplateFormFields.previewUrl,
                    caption: this.supWhatsappMessageTemplateFormFields.caption
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
