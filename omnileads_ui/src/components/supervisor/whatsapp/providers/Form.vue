<template>
  <div class="card">
    <div class="grid formgrid mt-4">
      <div class="field col-12">
        <label
          id="whatsapp_provider_nombre"
          :class="{
            'p-error': v$.supWhatsappProviderForm.nombre.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.provider.nombre") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="whatsapp_provider_nombre"
            :class="{
              'p-invalid':
                v$.supWhatsappProviderForm.nombre.$invalid && submitted,
            }"
            v-model="v$.supWhatsappProviderForm.nombre.$model"
          />
        </div>
        <small
          v-if="
            (v$.supWhatsappProviderForm.nombre.$invalid && submitted) ||
            v$.supWhatsappProviderForm.nombre.$pending.$response
          "
          class="p-error"
          >{{
            v$.supWhatsappProviderForm.nombre.required.$message.replace(
              "Value",
              $t("models.whatsapp.provider.nombre")
            )
          }}</small
        >
      </div>
    </div>
    <div class="grid formgrid mt-4">
      <div class="field col-12">
        <label
          id="whatsapp_provider_proveedor"
          :class="{
            'p-error':
              v$.supWhatsappProviderForm.tipo_proveedor.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.provider.tipo_proveedor") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-sitemap"></i>
          </span>
          <Dropdown
            id="whatsapp_provider_proveedor"
            v-model="v$.supWhatsappProviderForm.tipo_proveedor.$model"
            class="w-full"
            :class="{
              'p-invalid':
                v$.supWhatsappProviderForm.tipo_proveedor.$invalid && submitted,
            }"
            :options="providers"
            placeholder="-----"
            optionLabel="name"
            optionValue="value"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
        </div>
        <small
          v-if="
            (v$.supWhatsappProviderForm.tipo_proveedor.$invalid && submitted) ||
            v$.supWhatsappProviderForm.tipo_proveedor.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.supWhatsappProviderForm.tipo_proveedor.required.$message.replace(
              "Value",
              $t("models.whatsapp.provider.tipo_proveedor")
            )
          }}
        </small>
      </div>
    </div>
    <div class="field col-12" v-if="supWhatsappProviderForm.tipo_proveedor === providersType.META">
      <div class="grid formgrid mt-4">
        <div class="field col-12">
          <label
            :class="{
              'p-error':
                errors.business_id &&
                submitted,
            }"
            >{{ $t("models.whatsapp.provider.configuracion.business_id") }}*</label
          >
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-key"></i>
            </span>
            <Password
              toggleMask
              :feedback="false"
              :class="{
                'p-invalid': errors.business_id && submitted,
              }"
              v-model="v$.supWhatsappProviderForm.business_id.$model"
            />
          </div>
        </div>
      </div>
      <div class="grid formgrid mt-4">
        <div class="field col-12">
          <label
            :class="{
              'p-error':
                errors.access_token &&
                submitted,
            }"
            >{{ $t("models.whatsapp.provider.configuracion.access_token") }}*</label
          >
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-key"></i>
            </span>
            <Password
              toggleMask
              :feedback="false"
              :class="{
                'p-invalid':
                  errors.access_token && submitted,
              }"
              v-model="v$.supWhatsappProviderForm.access_token.$model"
            />
          </div>
        </div>
      </div>
    </div>
    <div class="field col-12" v-if="supWhatsappProviderForm.tipo_proveedor === providersType.GUPSHUP">
      <div class="grid formgrid mt-4">
        <div class="field col-12">
          <label
            :class="{
              'p-error':
                errors.api_key &&
                submitted,
            }"
            >{{ $t("models.whatsapp.provider.configuracion.api_key") }}*</label>
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-key"></i>
            </span>
            <Password
              toggleMask
              :feedback="false"
              :class="{
                'p-invalid':
                  errors.api_key &&
                  submitted,
              }"
              v-model="v$.supWhatsappProviderForm.api_key.$model"
            />
          </div>
        </div>
      </div>
      <div class="grid formgrid mt-4">
        <div class="field col-12">
          <label
            id="whatsapp_provider_email_partner"
            :class="{
              'p-error': v$.supWhatsappProviderForm.email_partner.$invalid && submitted,
            }"
            >{{ $t("models.whatsapp.provider.configuracion.email_partner") }}</label
          >
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-at"></i>
            </span>
            <InputText
              id="whatsapp_provider_email_partner"
              :class="{
                'p-invalid':
                  v$.supWhatsappProviderForm.email_partner.$invalid && submitted,
              }"
              v-model="v$.supWhatsappProviderForm.email_partner.$model"
            />
          </div>
          <small
            v-if="
              (v$.supWhatsappProviderForm.email_partner.$invalid && submitted) ||
              v$.supWhatsappProviderForm.email_partner.$pending.$response
            "
            class="p-error"
            >{{
              v$.supWhatsappProviderForm.email_partner.required.$message.replace(
                "Value",
                $t("models.whatsapp.provider.email_partner")
              )
            }}</small
          >
        </div>
      </div>
      <div class="grid formgrid mt-4">
        <div class="field col-12">
          <label
            :class="{
              'p-error':
                v$.supWhatsappProviderForm.password_partner.$invalid &&
                submitted,
            }"
            >{{ $t("models.whatsapp.provider.configuracion.password_partner") }}</label
          >
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-key"></i>
            </span>
            <Password
              :feedback="false"
              :class="{
                'p-invalid':
                  v$.supWhatsappProviderForm.password_partner.$invalid &&
                  submitted,
              }"
              v-model="v$.supWhatsappProviderForm.password_partner.$model"
            />
          </div>
          <small
            v-if="
              (v$.supWhatsappProviderForm.password_partner.$invalid &&
                submitted) ||
              v$.supWhatsappProviderForm.password_partner.$pending.$response
            "
            class="p-error"
            >{{
              v$.supWhatsappProviderForm.password_partner.required.$message.replace(
                "Value",
                $t("models.whatsapp.provider.configuracion.password_partner")
              )
            }}</small
          >
        </div>
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap mt-4">
      <div class="flex align-items-center">
        <Button
          class="p-button-danger p-button-outlined mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal"
        />
        <Button
          :label="$t('globals.save')"
          icon="pi pi-save"
          @click="saveProvider(!v$.$invalid)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { FilterMatchMode } from 'primevue/api';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';
import { PROVIDER_TYPES } from '@/globals/supervisor/whatsapp/provider';
import { HTTP_STATUS } from '@/globals';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            supWhatsappProviderForm: {
                nombre: { required },
                tipo_proveedor: { required },
                api_key: { },
                email_partner: { },
                password_partner: { },
                business_id: { },
                access_token: { },
            }
        };
    },
    inject: ['$helpers'],
    props: {
        formToCreate: {
            type: Boolean,
            default: true
        }
    },
    data () {
        return {
            supWhatsappProviderForm: {
                id: null,
                nombre: '',
                tipo_proveedor: 0,
                business_id: '',
                access_token: '',
                api_key: '',
                email_partner: '',
                password_partner: ''
            },
            errors: {},
            submitted: false,
            filters: null,
            providers: [
                {
                  name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.provider.types.meta'),
                    value: PROVIDER_TYPES.META
                },
                {
                    name: this.$t('forms.whatsapp.provider.types.gupshup'),
                    value: PROVIDER_TYPES.GUPSHUP
                }
            ],
            providersType: {
                META: PROVIDER_TYPES.META,
                GUPSHUP: PROVIDER_TYPES.GUPSHUP
            }
        };
    },
    created () {
        this.initializeData();
    },
    computed: {
        ...mapState(['supWhatsappProvider'])
    },
    methods: {
        ...mapActions([
            'createWhatsappProvider',
            'updateWhatsappProvider',
            'initWhatsappProviders'
        ]),
        closeModal () {
            this.$emit('closeModalEvent');
        },
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        initFormData () {
            this.supWhatsappProviderForm.id = this.supWhatsappProvider.id;
            this.supWhatsappProviderForm.nombre = this.supWhatsappProvider.nombre;
            this.supWhatsappProviderForm.tipo_proveedor = this.supWhatsappProvider.tipo_proveedor;
            if (this.supWhatsappProvider.configuracion){
              if (this.supWhatsappProvider.tipo_proveedor === PROVIDER_TYPES.GUPSHUP) {
                this.supWhatsappProviderForm.api_key = this.supWhatsappProvider.configuracion.api_key;
                this.supWhatsappProviderForm.email_partner = this.supWhatsappProvider.configuracion.email_partner;
                this.supWhatsappProviderForm.password_partner = this.supWhatsappProvider.configuracion.password_partner;
              } else if (this.supWhatsappProvider.tipo_proveedor === PROVIDER_TYPES.META){
                  this.supWhatsappProviderForm.business_id = this.supWhatsappProvider.configuracion.business_id;
                  this.supWhatsappProviderForm.access_token = this.supWhatsappProvider.configuracion.access_token;
                }
            }
        },
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        async saveProvider (isFormValid) {
            this.submitted = true;
            if (!isFormValid || !this.validateForm()) {
                return null;
            }
            var response = null;
            var configuracion = {}
            if (this.supWhatsappProviderForm.tipo_proveedor === PROVIDER_TYPES.GUPSHUP){
                configuracion = {
                    api_key: this.supWhatsappProviderForm.api_key,
                    email_partner: this.supWhatsappProviderForm.email_partner,
                    password_partner: this.supWhatsappProviderForm.password_partner
                };
            }
            else if (this.supWhatsappProviderForm.tipo_proveedor === PROVIDER_TYPES.META){
                configuracion = {
                    business_id: this.supWhatsappProviderForm.business_id,
                    access_token: this.supWhatsappProviderForm.access_token
                };
            }
            const form = {
                name: this.supWhatsappProviderForm.nombre,
                provider_type: this.supWhatsappProviderForm.tipo_proveedor,
                configuration: configuracion
            };
            if (this.formToCreate) {
                response = await this.createWhatsappProvider(
                    form
                );
            } else {
                response = await this.updateWhatsappProvider({
                    id: this.supWhatsappProvider.id,
                    data: form
                });
            }
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initWhatsappProviders();
                this.$router.push({ name: 'supervisor_whatsapp_providers' });
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
            this.closeModal();
        },
        validateForm() {
          this.errors = {};
          if(this.supWhatsappProviderForm.tipo_proveedor === PROVIDER_TYPES.META){
            if (!this.supWhatsappProviderForm.business_id){
              this.errors.business_id = true;
            }
            if (!this.supWhatsappProviderForm.access_token){
              this.errors.access_token = true;
            }
          }else if(this.supWhatsappProviderForm.tipo_proveedor === PROVIDER_TYPES.GUPSHUP){
            if (!this.supWhatsappProviderForm.api_key){
              this.errors.api_key = true;
            }
          }
          return Object.keys(this.errors).length === 0;
        },
    },
    watch: {
        supWhatsappProvider: {
            handler () {
                if (this.supWhatsappProvider) {
                    this.initFormData();
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
