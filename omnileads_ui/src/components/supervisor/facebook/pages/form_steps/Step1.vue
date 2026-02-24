<template>
  <div class="card">
    <div class="fluid grid formgrid mt-4">
      <div class="field col-6">
        <label
          :class="{
            'p-error':
              (v$.supFacebookPage.name.$invalid && submitted) ||
              repeatedFormName,
          }"
          >{{ $t("models.facebook.page.name") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            :class="{
              'p-invalid':
                (v$.supFacebookPage.name.$invalid && submitted) ||
                repeatedFormName,
            }"
            @input="validateFormName"
            :placeholder="$t('forms.form.enter_name')"
            v-model="v$.supFacebookPage.name.$model"
          />
        </div>
        <small
          v-if="
            (v$.supFacebookPage.name.$invalid && submitted) ||
            v$.supFacebookPage.name.$pending.$response
          "
          class="p-error"
          >{{
            v$.supFacebookPage.name.required.$message.replace(
              "Value",
              $t("models.facebook.page.name")
            )
          }}</small
        >
        <small v-if="repeatedFormName" class="p-error">{{
          $t("forms.form.validations.repeated_form_name")
        }}</small>
      </div>
      <div class="field col-6">
        <label
          :class="{
            'p-error': v$.supFacebookPage.description.$invalid && submitted,
          }"
          >{{ $t("models.facebook.page.description") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-star"></i>
          </span>
          <Textarea
            :class="{
              'p-invalid':
                v$.supFacebookPage.description.$invalid && submitted,
            }"
            :placeholder="$t('forms.form.enter_description')"
            v-model="v$.supFacebookPage.description.$model"
          />
        </div>
        <small
          v-if="
            (v$.supFacebookPage.description.$invalid && submitted) ||
            v$.supFacebookPage.description.$pending.$response
          "
          class="p-error"
          >{{
            v$.supFacebookPage.description.required.$message.replace(
              "Value",
              $t("models.facebook.page.description")
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
            supFacebookPage: {
                name: { required },
                description: { required }
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
        ...mapState(['supFacebookPage', 'forms'])
    },
    methods: {
        validateFormName () {
            this.repeatedFormName =
        this.forms.find((f) => f.name === this.supFacebookPage.name) !==
        undefined;
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
