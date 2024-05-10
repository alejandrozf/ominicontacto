<template>
  <div class="card">
    <div class="grid formgrid">
      <div class="field col-12">
        <label
          :class="{
            'p-error': v$.form.text.$invalid && submitted,
          }"
          >{{ $t("forms.whatsapp.message_template.fields.text") }}*</label
        >
        <div class="p-inputgroup mt-1">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <Textarea
            :class="{
              'p-invalid': v$.form.text.$invalid && submitted,
            }"
            :autoResize="true"
            rows="5"
            cols="30"
            v-model="v$.form.text.$model"
          />
        </div>
        <small
          v-if="
            (v$.form.text.$invalid && submitted) ||
            v$.form.text.$pending.$response
          "
          class="p-error"
          >{{
            v$.form.text.required.$message.replace(
              "Value",
              $t("forms.whatsapp.message_template.fields.text")
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
                text: { required }
            }
        };
    },
    data () {
        return {
            form: {
                type: 'text',
                text: ''
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
                    type: 'text',
                    text: this.supWhatsappMessageTemplateFormFields.text
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
