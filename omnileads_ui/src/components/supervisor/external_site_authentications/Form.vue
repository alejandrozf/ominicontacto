<template>
  <div class="card">
    <div class="grid formgrid mt-4">
      <div class="field col-6">
        <label
          id="external_site_authentication_name"
          :class="{
            'p-error':
              v$.externalSiteAuthentication.nombre.$invalid && submitted,
          }"
          >{{ $t("models.external_site_authentication.name") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="external_site_authentication_name"
            v-model="v$.externalSiteAuthentication.nombre.$model"
            :class="{
              'p-invalid':
                v$.externalSiteAuthentication.nombre.$invalid && submitted,
            }"
            :placeholder="
              $t('forms.external_site_authentication.placeholders.name')
            "
          />
        </div>
        <small
          v-if="
            (v$.externalSiteAuthentication.nombre.$invalid && submitted) ||
            v$.externalSiteAuthentication.nombre.$pending.$response
          "
          class="p-error"
          >{{
            v$.externalSiteAuthentication.nombre.required.$message.replace(
              "Value",
              $t("models.external_site_authentication.name")
            )
          }}</small
        >
      </div>
      <div class="field col-6">
        <label
          id="external_site_authentication_url"
          :class="{
            'p-error': v$.externalSiteAuthentication.url.$invalid && submitted,
          }"
          >{{ $t("models.external_site_authentication.url") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-link"></i>
          </span>
          <InputText
            id="external_site_authentication_url"
            :class="{
              'p-invalid':
                v$.externalSiteAuthentication.url.$invalid && submitted,
            }"
            :placeholder="
              $t('forms.external_site_authentication.placeholders.url')
            "
            v-model="v$.externalSiteAuthentication.url.$model"
          />
        </div>
        <small
          v-if="
            (v$.externalSiteAuthentication.url.$invalid && submitted) ||
            v$.externalSiteAuthentication.url.$pending.$response
          "
          class="p-error"
        >
          <span
            v-for="error of v$.externalSiteAuthentication.url.$errors"
            :key="error.$uid"
          >
            {{
              error.$message.replace(
                "Value",
                $t("models.external_site_authentication.url")
              )
            }}
          </span>
        </small>
      </div>
    </div>
    <div class="grid formgrid mt-2">
      <div class="field col-4">
        <label
          id="external_site_authentication_username"
          :class="{
            'p-error':
              v$.externalSiteAuthentication.username.$invalid && submitted,
          }"
          >{{ $t("models.external_site_authentication.username") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-user"></i>
          </span>
          <InputText
            id="external_site_authentication_username"
            v-model="v$.externalSiteAuthentication.username.$model"
            :class="{
              'p-invalid':
                v$.externalSiteAuthentication.username.$invalid && submitted,
            }"
            :placeholder="
              $t('forms.external_site_authentication.placeholders.username')
            "
          />
        </div>
        <small
          v-if="
            (v$.externalSiteAuthentication.username.$invalid && submitted) ||
            v$.externalSiteAuthentication.username.$pending.$response
          "
          class="p-error"
          >{{
            v$.externalSiteAuthentication.username.required.$message.replace(
              "Value",
              $t("models.external_site_authentication.username")
            )
          }}</small
        >
      </div>
      <div class="field col-4">
        <label
          id="external_site_authentication_password"
          :class="{
            'p-error':
              v$.externalSiteAuthentication.password.$invalid && submitted,
          }"
          >{{ $t("models.external_site_authentication.password") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-lock"></i>
          </span>
          <Password
            id="external_site_authentication_password"
            v-model="v$.externalSiteAuthentication.password.$model"
            toggleMask
            :feedback="false"
            :class="{
              'p-invalid':
                v$.externalSiteAuthentication.password.$invalid && submitted,
            }"
          />
        </div>
        <small
          v-if="
            (v$.externalSiteAuthentication.password.$invalid && submitted) ||
            v$.externalSiteAuthentication.password.$pending.$response
          "
          class="p-error"
          >{{
            v$.externalSiteAuthentication.password.required.$message.replace(
              "Value",
              $t("models.external_site_authentication.password")
            )
          }}</small
        >
      </div>
      <div class="field col-4">
        <label
          id="external_site_authentication_campo_ssl_estricto"
          >{{ $t("models.external_site_authentication.ssl_estricto") }}</label
        >
        <div class="p-inputgroup mt-2">
          <Checkbox
            id="external_site_authentication_campo_ssl_estricto"
            v-model="v$.externalSiteAuthentication.ssl_estricto.$model"
            :binary="true"
          />
        </div>
      </div>
    </div>
    <div class="grid formgrid mt-2">
      <div class="field col-4">
        <label
          id="external_site_authentication_campo_token"
          :class="{ 'p-error': invalid_name_campo_token }"
          >{{ $t("models.external_site_authentication.campo_token") }}</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-id-card"></i>
          </span>
          <InputText
            id="external_site_authentication_campo_token"
            v-model="externalSiteAuthentication.campo_token"
            :class="{ 'p-invalid': invalid_name_campo_token }"
            @input='campoTokenEventChange'
            :placeholder="
              $t('forms.external_site_authentication.placeholders.campo_token')
            "
          />
        </div>
        <small class="text-muted">{{
          $t("forms.external_site_authentication.helpers.campo_token")
        }}</small>
        <br>
        <small v-if="invalid_name_campo_token" class="p-error">{{
            $t(
              "forms.external_site_authentication.validations.invalid_name_campo_token"
            )
        }}</small>
      </div>
      <div class="field col-4">
        <label
          id="external_site_authentication_campo_duracion"
          :class="{ 'p-error': invalid_campo_duracion || invalid_name_campo_duracion, 'text-muted': disable_campo_duracion }"
          >{{ $t("models.external_site_authentication.campo_duracion") }}</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-calendar"></i>
          </span>
          <InputText
            id="external_site_authentication_campo_duracion"
            v-model="externalSiteAuthentication.campo_duracion"
            :class="{ 'p-invalid': invalid_campo_duracion || invalid_name_campo_duracion }"
            :disabled="disable_campo_duracion"
            @input='campoDuracionEventChange'
            :placeholder="
              $t(
                'forms.external_site_authentication.placeholders.campo_duracion'
              )
            "
          />
        </div>
        <small class="text-muted">{{
          $t("forms.external_site_authentication.helpers.campo_duracion")
        }}</small>
        <br>
        <small v-if="invalid_campo_duracion" class="p-error">{{
            $t(
              "forms.external_site_authentication.validations.invalid_campo_duracion"
            )
        }}</small>
        <br>
        <small v-if="invalid_name_campo_duracion" class="p-error">{{
            $t(
              "forms.external_site_authentication.validations.invalid_name_campo_duracion"
            )
        }}</small>
      </div>
      <div class="field col-4">
        <label
          id="external_site_authentication_duracion"
          >{{ $t("models.external_site_authentication.duracion") }}</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-clock"></i>
          </span>
          <InputNumber
            id="external_site_authentication_duracion"
            v-model="externalSiteAuthentication.duracion"
            :min="0"
            mode="decimal"
            :useGrouping="false"
            :disabled="disable_duracion"
            @input='duracionEventChange'
            :placeholder="
              $t('forms.external_site_authentication.placeholders.duracion')
            "
          />
        </div>
        <small class="text-muted">{{
          $t("forms.external_site_authentication.helpers.duracion")
        }}</small>
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap">
      <div class="flex align-items-center gap-2">
        <Button
          :label="$t('views.external_site_authentication.test_auth.label')"
          :disabled="v$.externalSiteAuthentication.$invalid"
          icon="pi pi-key"
          class="mt-4 p-button-outlined"
          @click="test_auth()"
        />
        <Button
          :label="$t('globals.save')"
          icon="pi pi-save"
          class="mt-4"
          @click="save(!v$.$invalid)"
        />
      </div>
    </div>
    <Message v-for="msg of messages" :severity="msg.severity" :key="msg.content">
      {{ msg.content }}
    </Message>
  </div>
</template>

<script>
import { FilterMatchMode } from 'primevue/api';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';
import { HTTP_STATUS } from '@/globals';

export default {
    setup: () => ({ v$: useVuelidate({ $scope: false }) }),
    validations () {
        return {
            externalSiteAuthentication: {
                nombre: { required },
                url: { required },
                username: { required },
                password: { required },
                ssl_estricto: { required }

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
            submitted: false,
            filters: null,
            invalid_campo_duracion: false,
            invalid_name_campo_token: false,
            invalid_name_campo_duracion: false,
            disable_campo_duracion: true,
            disable_duracion: false,
            messages: [],
            regexAlfanumeric: new RegExp('^[a-zA-Z0-9_]+$')
        };
    },
    created () {
        this.initData();
    },
    computed: {
        ...mapState(['externalSiteAuthentication'])
    },
    methods: {
        ...mapActions([
            'createExternalSiteAuthentication',
            'testExternalSiteAuthentication',
            'updateExternalSiteAuthentication',
            'initExternalSiteAuthentications'
        ]),
        clearFilter () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        initData () {
            this.submitted = false;
            this.invalid_campo_duracion = false;
            this.invalid_name_campo_token = false;
            this.invalid_name_campo_duracion = false;
            this.disable_campo_duracion = true;
            this.disable_duracion = false;
        },
        campoTokenEventChange () {
            if (this.regexAlfanumeric.test(this.externalSiteAuthentication.campo_token)) {
                this.invalid_name_campo_token = false;
            } else {
                this.invalid_name_campo_token = true;
            }
        },
        campoDuracionEventChange () {
            this.externalSiteAuthentication.duracion = 0;
            if (this.externalSiteAuthentication.campo_duracion) {
                if (this.regexAlfanumeric.test(this.externalSiteAuthentication.campo_duracion)) {
                    this.invalid_name_campo_duracion = false;
                } else {
                    this.invalid_name_campo_duracion = true;
                }
                this.invalid_campo_duracion = false;
                this.disable_duracion = true;
            } else {
                this.invalid_campo_duracion = true;
                this.disable_duracion = false;
            }
        },
        duracionEventChange (event) {
            this.externalSiteAuthentication.campo_duracion = '';
            if (event.value === null || event.value === 0) {
                this.externalSiteAuthentication.duracion = 0;
                this.disable_campo_duracion = false;
                this.invalid_campo_duracion = true;
            } else {
                this.externalSiteAuthentication.duracion = event.value;
                this.disable_campo_duracion = true;
                this.invalid_campo_duracion = false;
            }
        },
        async test_auth () {
            const response = await this.testExternalSiteAuthentication(this.externalSiteAuthentication);
            this.messages.push({
                severity: response.status === HTTP_STATUS.SUCCESS ? 'success' : 'error',
                content: response.message
            });
        },
        async save (isFormValid) {
            this.submitted = true;
            if (!isFormValid || this.invalid_campo_duracion || this.invalid_name_campo_token || this.invalid_name_campo_duracion) {
                return null;
            }
            var response = null;
            if (this.formToCreate) {
                response = await this.createExternalSiteAuthentication(
                    this.externalSiteAuthentication
                );
            } else {
                response = await this.updateExternalSiteAuthentication({
                    id: this.externalSiteAuthentication.id,
                    data: this.externalSiteAuthentication
                });
            }
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                this.initData();
                await this.initExternalSiteAuthentications();
                this.$router.push({ name: 'supervisor_external_site_authentications' });
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
    },
    watch: {
        externalSiteAuthentication: {
            handler () {
                const duracion = this.externalSiteAuthentication.duracion;
                if (duracion === null || duracion === 0) {
                    this.disable_campo_duracion = false;
                } else {
                    this.disable_campo_duracion = true;
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>

<style scoped>
.text-muted {
  opacity: 0.5;
}
</style>
