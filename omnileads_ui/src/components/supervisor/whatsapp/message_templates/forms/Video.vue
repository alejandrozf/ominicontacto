<template>
  <div class="card">
    <div class="grid formgrid">
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
          $t("forms.whatsapp.message_template.help_text.video.url")
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
          $t("forms.whatsapp.message_template.help_text.video.caption")
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
                url: { required },
                caption: { required }
            }
        };
    },
    data () {
        return {
            form: {
                type: 'image',
                url: '',
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
                    url: this.supWhatsappMessageTemplateFormFields.url,
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
