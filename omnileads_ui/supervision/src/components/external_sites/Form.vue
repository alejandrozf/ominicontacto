<template>
  <div class="card">
    <div class="grid formgrid mt-4">
      <div class="field col-6">
        <label
          id="external_site_name"
          :class="{
            'p-error': v$.externalSiteForm.nombre.$invalid && submitted,
          }"
          >{{ $t("models.external_site.name") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="external_site_name"
            :class="{
              'p-invalid': v$.externalSiteForm.nombre.$invalid && submitted,
            }"
            v-model="v$.externalSiteForm.nombre.$model"
          />
        </div>
        <small
          v-if="
            (v$.externalSiteForm.nombre.$invalid && submitted) ||
            v$.externalSiteForm.nombre.$pending.$response
          "
          class="p-error"
          >{{
            v$.externalSiteForm.nombre.required.$message.replace(
              "Value",
              $t("models.external_site.name")
            )
          }}</small
        >
      </div>
      <div class="field col-6">
        <label
          id="external_site_url"
          :class="{ 'p-error': v$.externalSiteForm.url.$invalid && submitted }"
          >{{ $t("models.external_site.url") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-link"></i>
          </span>
          <InputText
            id="external_site_url"
            :class="{
              'p-invalid': v$.externalSiteForm.url.$invalid && submitted,
            }"
            v-model="v$.externalSiteForm.url.$model"
          />
        </div>
        <small
          v-if="
            (v$.externalSiteForm.url.$invalid && submitted) ||
            v$.externalSiteForm.url.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.externalSiteForm.url.required.$message.replace(
              "Value",
              $t("models.external_site.url")
            )
          }}
        </small>
      </div>
    </div>
    <div class="grid formgrid mt-4">
      <div class="field col-6">
        <label>{{ $t("models.external_site.trigger") }}</label>
        <Dropdown
          v-model="externalSiteForm.disparador"
          class="w-full"
          :options="triggers"
          placeholder="Servidor"
          optionLabel="name"
          optionValue="value"
          @change="triggerEvent"
          :emptyFilterMessage="$t('globals.without_data')"
          :filter="true"
          v-bind:filterPlaceholder="
            $t('globals.find_by', { field: $tc('globals.name') }, 1)
          "
        />
      </div>
      <div class="field col-6">
        <label>{{ $t("models.external_site.method") }}</label>
        <Dropdown
          v-model="externalSiteForm.metodo"
          class="w-full"
          :options="methods"
          optionLabel="name"
          placeholder="GET"
          optionValue="value"
          @change="methodEvent"
          :emptyFilterMessage="$t('globals.without_data')"
          :filter="true"
          v-bind:filterPlaceholder="
            $t('globals.find_by', { field: $tc('globals.name') }, 1)
          "
        />
      </div>
    </div>
    <div class="fluid grid formgrid mt-4">
      <div class="field col-6">
        <label>{{ $t("models.external_site.format") }}</label>
        <Dropdown
          v-model="externalSiteForm.formato"
          class="w-full"
          :options="formats"
          optionLabel="name"
          optionValue="value"
          placeholder="-------"
          @change="formatEvent"
          :emptyFilterMessage="$t('globals.without_data')"
          :filter="true"
          :disabled="status_format"
          v-bind:filterPlaceholder="
            $t('globals.find_by', { field: $tc('globals.name') }, 1)
          "
        />
        <small v-if="invalid_format" class="p-error">
          Si el metodo es POST debe elegirse un formato valido
        </small>
      </div>
      <div class="field col-6">
        <label>{{ $t("models.external_site.objective") }}</label>
        <Dropdown
          v-model="externalSiteForm.objetivo"
          class="w-full"
          :options="objectives"
          optionLabel="name"
          optionValue="value"
          placeholder="-------"
          disbled
          :emptyFilterMessage="$t('globals.without_data')"
          :filter="true"
          :disabled="status_objective"
          v-bind:filterPlaceholder="
            $t('globals.find_by', { field: $tc('globals.name') }, 1)
          "
        />
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap">
      <div class="flex align-items-center">
        <Button
          :label="$t('globals.save')"
          icon="pi pi-save"
          class="mt-4"
          @click="saveExternalSite(!v$.$invalid)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { FilterMatchMode } from 'primevue/api';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions } from 'vuex';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            externalSiteForm: {
                nombre: { required },
                url: { required }
            }
        };
    },
    inject: ['$helpers'],
    props: {
        formToCreate: {
            type: Boolean,
            default: true
        },
        externalSite: {
            type: Object,
            default () {
                return {
                    nombre: '',
                    url: '',
                    metodo: 0,
                    disparador: 0,
                    formato: null,
                    objetivo: null
                };
            }
        }
    },
    data () {
        return {
            externalSiteForm: {
                nombre: '',
                url: '',
                metodo: 0,
                disparador: 0,
                formato: null,
                objetivo: null
            },
            submitted: false,
            filters: null,
            invalid_format: false,
            status_format: true,
            status_objective: true,
            methods: [
                { name: 'GET', value: 1 },
                { name: 'POST', value: 2 }
            ],
            objectives: [
                { name: '-------', value: null },
                { name: 'Embebido', value: 1 },
                { name: 'Nueva pestaña', value: 2 }
            ],
            formats: [
                { name: '-------', value: null },
                { name: 'multipart/form-data', value: 1 },
                { name: 'application/x-www-form-urlencoded', value: 2 },
                { name: 'text/plain', value: 3 },
                { name: 'application/json', value: 4 }
            ],
            triggers: [
                { name: 'Agente', value: 1 },
                { name: 'Automático', value: 2 },
                { name: 'Servidor', value: 3 },
                { name: 'Calificación', value: 4 }
            ]
        };
    },
    created () {
        this.initializeData();
    },
    methods: {
        ...mapActions(['createExternalSite', 'updateExternalSite']),
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        initFormData () {
            this.externalSiteForm.nombre = this.externalSite.nombre;
            this.externalSiteForm.url = this.externalSite.url;
            this.externalSiteForm.metodo = this.externalSite.metodo;
            this.externalSiteForm.disparador = this.externalSite.disparador;
            this.externalSiteForm.formato = this.externalSite.formato;
            this.externalSiteForm.objetivo = this.externalSite.objetivo;
            if ([1, 0].includes(this.externalSite.metodo)) {
                this.externalSiteForm.formato = null;
                this.status_format = true;
            } else {
                this.status_format = false;
            }
            if ([3, 0].includes(this.externalSite.disparador)) {
                this.externalSiteForm.objetivo = null;
                this.status_objective = true;
            } else {
                this.status_objective = false;
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
        triggerEvent () {
            if (
                [3, 0].includes(this.externalSiteForm.disparador) ||
        this.externalSiteForm.formato === 4
            ) {
                this.status_objective = true;
                this.externalSiteForm.objetivo = null;
            } else {
                this.status_objective = false;
                this.externalSiteForm.objetivo = 1;
            }
        },
        methodEvent () {
            if ([1, 0].includes(this.externalSiteForm.metodo)) {
                this.status_format = true;
                this.externalSiteForm.formato = null;
            } else {
                this.status_format = false;
                this.externalSiteForm.formato = 1;
                if (this.externalSiteForm.disparador === 3) {
                    this.status_objective = true;
                }
            }
        },
        formatEvent () {
            if (
                this.externalSiteForm.formato !== 4 &&
        [3, 0].includes(this.externalSiteForm.disparador)
            ) {
                this.status_objective = true;
                this.externalSiteForm.objetivo = null;
            } else if (
                this.externalSiteForm.formato === 4 &&
        ![3, 0].includes(this.externalSiteForm.disparador)
            ) {
                this.status_objective = true;
                this.externalSiteForm.objetivo = null;
            } else {
                this.status_objective = false;
                this.externalSiteForm.objetivo = 1;
            }
        },
        async saveExternalSite (isFormValid) {
            this.submitted = true;
            if (this.externalSiteForm.disparador === 0) {
                this.externalSiteForm.disparador = 3;
            }
            if (this.externalSiteForm.metodo === 0) {
                this.externalSiteForm.metodo = 1;
            }
            if (!isFormValid) {
                if (
                    this.externalSiteForm.metodo === 2 &&
          this.externalSiteForm.formato === null
                ) {
                    this.invalid_format = true;
                } else {
                    this.invalid_format = false;
                }
                return null;
            }
            if (
                this.externalSiteForm.metodo === 2 &&
        this.externalSiteForm.formato === null
            ) {
                this.invalid_format = true;
                return null;
            }
            this.invalid_format = false;
            var response = null;
            if (this.formToCreate) {
                response = await this.createExternalSite(this.externalSiteForm);
            } else {
                response = await this.updateExternalSite({
                    id: this.externalSite.id,
                    data: this.externalSiteForm
                });
            }
            const { status, message } = response;
            if (status === 'SUCCESS') {
                this.$router.push({ name: 'external_sites' });
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
        externalSite: {
            handler () {
                this.initFormData();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
