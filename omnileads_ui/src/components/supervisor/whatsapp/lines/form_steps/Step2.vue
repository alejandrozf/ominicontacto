<template>
  <div class="card">
    <div class="grid formgrid">
      <div class="field col-12">
        <Fieldset>
          <template #legend>
            {{ $t("views.whatsapp.line.step2.sender") }}
          </template>
          <div>
            <label v-if="supWhatsappLine.provider_type===providersType.GUPSHUP"
              :class="{
                'p-error': v$.supWhatsappLine.numero.$invalid && submitted,
              }"
              > 
              {{ $t("models.whatsapp.line.numero") }}*</label>
            <label v-if="supWhatsappLine.provider_type===providersType.META"
              :class="{
                'p-error': v$.supWhatsappLine.numero.$invalid && submitted,
              }"
              > 
              {{ $t("models.whatsapp.line.phone_id") }}*</label>

            <div class="p-inputgroup mt-2">
              <span class="p-inputgroup-addon">
                <i class="pi pi-phone"></i>
              </span>
              <InputText
                placeholder="999-999-9999"
                :class="{
                  'p-invalid': v$.supWhatsappLine.numero.$invalid && submitted,
                }"
                v-model="v$.supWhatsappLine.numero.$model"
              />
            </div>
            <small
              v-if="
                (v$.supWhatsappLine.numero.$invalid && submitted) ||
                v$.supWhatsappLine.numero.$pending.$response
              "
              class="p-error"
              >
              {{
                v$.supWhatsappLine.numero.required.$message.replace(
                  "Value",
                  $t("models.whatsapp.line.numero")
                )
              }}
            </small>
          </div>
        </Fieldset>
      </div>
    </div>
    <div class="grid formgrid mt-4">
      <div class="field col-12">
        <Fieldset>
          <template #legend>
            {{ $t("views.whatsapp.line.step2.app_info") }}
          </template>
          <div v-if="supWhatsappLine.provider_type===providersType.GUPSHUP" class="grid formgrid">
            <div class="field col-6">
              <label
                :class="{
                  'p-error':
                    v$.supWhatsappLine.configuracion.app_name.$invalid &&
                    submitted,
                }"
                >{{ $t("models.whatsapp.line.configuracion.app_name") }}*</label
              >
              <div class="p-inputgroup">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-list"></i>
                </span>
                <InputText
                  :class="{
                    'p-invalid':
                      v$.supWhatsappLine.configuracion.app_name.$invalid &&
                      submitted,
                  }"
                  :placeholder="$t('forms.form.enter_name')"
                  v-model="v$.supWhatsappLine.configuracion.app_name.$model"
                />
              </div>
              <small
                v-if="
                  (v$.supWhatsappLine.configuracion.app_name.$invalid &&
                    submitted) ||
                  v$.supWhatsappLine.configuracion.app_name.$pending.$response
                "
                class="p-error"
                >{{
                  v$.supWhatsappLine.configuracion.app_name.required.$message.replace(
                    "Value",
                    $t("models.whatsapp.line.configuracion.app_name")
                  )
                }}</small
              >
            </div>
            <div class="field col-6">
              <label
                :class="{
                  'p-error':
                    v$.supWhatsappLine.configuracion.app_id.$invalid &&
                    submitted,
                }"
                >{{ $t("models.whatsapp.line.configuracion.app_id") }}*</label
              >
              <div class="p-inputgroup">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-list"></i>
                </span>
                <Password
                  toggleMask
                  :feedback="false"
                  :class="{
                    'p-invalid':
                      v$.supWhatsappLine.configuracion.app_id.$invalid &&
                      submitted,
                  }"
                  :placeholder="$t('forms.form.enter_value')"
                  v-model="v$.supWhatsappLine.configuracion.app_id.$model"
                />
              </div>
              <small
                v-if="
                  (v$.supWhatsappLine.configuracion.app_id.$invalid &&
                    submitted) ||
                  v$.supWhatsappLine.configuracion.app_id.$pending.$response
                "
                class="p-error"
                >{{
                  v$.supWhatsappLine.configuracion.app_id.required.$message.replace(
                    "Value",
                    $t("models.whatsapp.line.configuracion.app_id")
                  )
                }}</small
              >
            </div>
          </div>
          <div v-if="supWhatsappLine.provider_type===providersType.META" class="grid formgrid">
            <div class="field col-6">
              <label
                :class="{
                  'p-error':
                    v$.supWhatsappLine.configuracion.app_name.$invalid &&
                    submitted,
                }"
                >{{ $t("models.whatsapp.line.configuracion.waba_id") }}*</label
              >
              <div class="p-inputgroup">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-list"></i>
                </span>
                <InputText
                  :class="{
                    'p-invalid':
                      v$.supWhatsappLine.configuracion.app_name.$invalid &&
                      submitted,
                  }"
                  :placeholder="$t('forms.form.enter_value')"
                  v-model="v$.supWhatsappLine.configuracion.app_name.$model"
                />
              </div>
              <small
                v-if="
                  (v$.supWhatsappLine.configuracion.app_name.$invalid &&
                    submitted) ||
                  v$.supWhatsappLine.configuracion.app_name.$pending.$response
                "
                class="p-error"
                >{{
                  v$.supWhatsappLine.configuracion.app_name.required.$message.replace(
                    "Value",
                    $t("models.whatsapp.line.configuracion.waba_id")
                  )
                }}</small
              >
            </div>
            <div class="field col-6">
              <label
                :class="{
                  'p-error':
                    v$.supWhatsappLine.configuracion.app_id.$invalid &&
                    submitted,
                }"
                >{{ $t("models.whatsapp.line.configuracion.app_id") }}*</label
              >
              <div class="p-inputgroup">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-list"></i>
                </span>
                <Password
                  toggleMask
                  :feedback="false"
                  :class="{
                    'p-invalid':
                      v$.supWhatsappLine.configuracion.app_id.$invalid &&
                      submitted,
                  }"
                  :placeholder="$t('forms.form.enter_value')"
                  v-model="v$.supWhatsappLine.configuracion.app_id.$model"
                />
              </div>
              <small
                v-if="
                  (v$.supWhatsappLine.configuracion.app_id.$invalid &&
                    submitted) ||
                  v$.supWhatsappLine.configuracion.app_id.$pending.$response
                "
                class="p-error"
                >{{
                  v$.supWhatsappLine.configuracion.app_id.required.$message.replace(
                    "Value",
                    $t("models.whatsapp.line.configuracion.app_id")
                  )
                }}</small
              >
            </div>
            <div class="field col-6">
              <label
                :class="{
                  'p-error':
                    v$.supWhatsappLine.configuracion.verification_token.$invalid &&
                    submitted,
                }"
                >{{ $t("models.whatsapp.line.configuracion.verification_token") }}*</label
              >
              <div class="p-inputgroup">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-list"></i>
                </span>
                <Password
                  toggleMask
                  :feedback="false"
                  :class="{
                    'p-invalid':
                      v$.supWhatsappLine.configuracion.verification_token.$invalid &&
                      submitted,
                  }"
                  :placeholder="$t('forms.form.enter_value')"
                  v-model="v$.supWhatsappLine.configuracion.verification_token.$model"
                />
              </div>
              <small
                v-if="
                  (v$.supWhatsappLine.configuracion.verification_token.$invalid &&
                    submitted) ||
                  v$.supWhatsappLine.configuracion.verification_token.$pending.$response
                "
                class="p-error"
                >{{
                  v$.supWhatsappLine.configuracion.verification_token.required.$message.replace(
                    "Value",
                    $t("models.whatsapp.line.configuracion.verification_token")
                  )
                }}</small
              >
            </div>

          </div>
        </Fieldset>
      </div>
    </div>
    <div class="flex justify-content-between flex-wrap">
      <div class="flex align-items-center justify-content-center">
        <Button
          :label="$t('globals.back')"
          icon="pi pi-angle-left"
          icon-pos="right"
          class="mt-4 p-button-secondary"
          @click="prevPage"
        />
      </div>
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
import { mapState, mapActions } from 'vuex';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { PROVIDER_TYPES } from '@/globals/supervisor/whatsapp/provider';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            supWhatsappLine: {
                numero: {
                    required
                },
                configuracion: {
                    app_name: { required },
                    app_id: { required },
                    verification_token: { }
                }
            }
        };
    },
    inject: ['$helpers'],
    data () {
        return {
            submitted: false,
            isPhoneValid: false,
            providersType: {
                META: PROVIDER_TYPES.META,
                GUPSHUP: PROVIDER_TYPES.GUPSHUP
            }
        };
    },
    computed: {
        ...mapState(['supWhatsappLine'])
    },
    methods: {
        ...mapActions(['']),
        validFields () {
            var formErrors = [];
            if (!this.supWhatsappLine.nombre || this.supWhatsappLine.nombre === '') {
                formErrors.push(
                    this.$tc('forms.whatsapp.line.validations.field_is_required', {
                        field: this.$t('models.whatsapp.line.nombre')
                    })
                );
            }
            if (!this.supWhatsappLine.proveedor) {
                formErrors.push(
                    this.$tc('forms.whatsapp.line.validations.field_is_required', {
                        field: this.$t('models.whatsapp.line.proveedor')
                    })
                );
            }
            if (formErrors.length > 0) {
                var errors = '<ul>';
                formErrors.forEach((e) => {
                    errors += `<li>${e}</li>`;
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
                return false;
            }
            return true;
        },
        nextPage (isFormValid) {
            this.submitted = true;
            if (isFormValid) {
                if (this.validFields()) {
                    this.$emit('next-page', { pageIndex: 1 });
                }
                return null;
            } else {
                return null;
            }
        },
        prevPage () {
            this.$emit('prev-page', { pageIndex: 1 });
        }
    },
    watch: {
        supWhatsappLine: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
