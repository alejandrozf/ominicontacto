<template>
  <div class="card">
    <div class="fluid grid formgrid mt-4">
      <div class="field col-6">
        <label
          :class="{
            'p-error':
              (v$.supWhatsappLine.nombre.$invalid && submitted) ||
              repeatedFormName,
          }"
          >{{ $t("models.whatsapp.line.nombre") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            :class="{
              'p-invalid':
                (v$.supWhatsappLine.nombre.$invalid && submitted) ||
                repeatedFormName,
            }"
            @input="validateFormName"
            :placeholder="$t('forms.form.enter_name')"
            v-model="v$.supWhatsappLine.nombre.$model"
          />
        </div>
        <small
          v-if="
            (v$.supWhatsappLine.nombre.$invalid && submitted) ||
            v$.supWhatsappLine.nombre.$pending.$response
          "
          class="p-error"
          >{{
            v$.supWhatsappLine.nombre.required.$message.replace(
              "Value",
              $t("models.whatsapp.line.nombre")
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
            'p-error': v$.supWhatsappLine.proveedor.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.line.proveedor") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-sitemap"></i>
          </span>
          <Dropdown
            v-model="v$.supWhatsappLine.proveedor.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.supWhatsappLine.proveedor.$invalid && submitted,
            }"
            :options="providers"
            :filter="true"
            :showClear="true"
            placeholder="-----"
            optionLabel="name"
            optionValue="id"
            optionGroupLabel="label"
            optionGroupChildren="items"
            :emptyFilterMessage="$t('globals.without_data')"
          />
        </div>
        <small
          v-if="
            (v$.supWhatsappLine.proveedor.$invalid && submitted) ||
            v$.supWhatsappLine.proveedor.$pending.$response
          "
          class="p-error"
          >{{
            v$.supWhatsappLine.proveedor.required.$message.replace(
              "Value",
              $t("models.whatsapp.line.proveedor")
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
import { PROVIDER_TYPES } from '@/globals/supervisor/whatsapp/provider';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            supWhatsappLine: {
                nombre: { required },
                proveedor: { required }
            }
        };
    },
    inject: ['$helpers'],
    data () {
        return {
            submitted: false,
            repeatedFormName: false,
            providers: [
                {
                    type: PROVIDER_TYPES.TWILIO,
                    label: this.$t('forms.whatsapp.provider.types.twilio'),
                    items: []
                },
                {
                    type: PROVIDER_TYPES.META,
                    label: this.$t('forms.whatsapp.provider.types.meta'),
                    items: []
                },
                {
                    type: PROVIDER_TYPES.GUPSHUP,
                    label: this.$t('forms.whatsapp.provider.types.gupshup'),
                    items: []
                }
            ]
        };
    },
    computed: {
        ...mapState(['supWhatsappLine', 'forms', 'supWhatsappProviders'])
    },
    methods: {
        validateFormName () {
            this.repeatedFormName =
        this.forms.find((f) => f.nombre === this.supWhatsappLine.nombre) !==
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
        },
        supWhatsappProviders: {
            handler () {
                if (this.supWhatsappProviders.length > 0) {
                    this.providers.find((p) => p.type === PROVIDER_TYPES.TWILIO).items =
            this.supWhatsappProviders.filter(
                (p) => p.provider_type === PROVIDER_TYPES.TWILIO
            );
                    this.providers.find((p) => p.type === PROVIDER_TYPES.META).items =
            this.supWhatsappProviders.filter(
                (p) => p.provider_type === PROVIDER_TYPES.META
            );
                    this.providers.find((p) => p.type === PROVIDER_TYPES.GUPSHUP).items =
            this.supWhatsappProviders.filter(
                (p) => p.provider_type === PROVIDER_TYPES.GUPSHUP
            );
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
