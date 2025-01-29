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
          <span
            v-for="error of v$.externalSiteForm.url.$errors"
            :key="error.$uid"
          >
            {{
              error.$message.replace(
                "Value",
                $t("models.external_site.url")
              )
            }}
          </span>
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
    <div class="fluid grid formgrid mt-4">
      <div class="field col-6">
        <label>{{ $t("globals.external_site_authentication") }}</label>
        <Dropdown
          v-model="externalSiteForm.autenticacion"
          class="w-full"
          :options="externalSiteAuthentications"
          optionLabel="nombre"
          optionValue="id"
          placeholder="-------"
          :emptyFilterMessage="$t('globals.without_data')"
          :filter="true"
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
import { mapActions, mapState } from 'vuex';
import { HTTP_STATUS } from '@/globals';

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
                    objetivo: null,
                    autenticacion: null
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
                objetivo: null,
                autenticacion: null
            },
            submitted: false,
            filters: null,
            invalid_format: false,
            status_format: true,
            status_objective: true,
            methods: [
                { name: this.$t('forms.external_site.methods.get'), value: 1 },
                { name: this.$t('forms.external_site.methods.post'), value: 2 }
            ],
            objectives: [
                { name: '-------', value: null },
                { name: this.$t('forms.external_site.objectives.opt1'), value: 1 },
                { name: this.$t('forms.external_site.objectives.opt2'), value: 2 }
            ],
            formats: [
                { name: '-------', value: null },
                { name: this.$t('forms.external_site.formats.opt1'), value: 1 },
                { name: this.$t('forms.external_site.formats.opt2'), value: 2 },
                { name: this.$t('forms.external_site.formats.opt3'), value: 3 },
                { name: this.$t('forms.external_site.formats.opt4'), value: 4 }
            ],
            triggers: [
                { name: this.$t('forms.external_site.triggers.opt1'), value: 1 },
                { name: this.$t('forms.external_site.triggers.opt2'), value: 2 },
                { name: this.$t('forms.external_site.triggers.opt3'), value: 3 },
                { name: this.$t('forms.external_site.triggers.opt4'), value: 4 },
                { name: this.$t('forms.external_site.triggers.opt5'), value: 5 },
            ]
        };
    },
    async created () {
        await this.initExternalSiteAuthentications();
        await this.initializeData();
    },
    computed: {
        ...mapState(['externalSiteAuthentications'])
    },
    methods: {
        ...mapActions(['createExternalSite', 'updateExternalSite', 'initExternalSiteAuthentications']),
        initializeData () {
            this.externalSiteAuthentications.splice(0, 0, { id: null, nombre: '------' });
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
            this.externalSiteForm.autenticacion = this.externalSite.autenticacion;
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
        handleObjetiveStatus () {
            if (
                [3, 0].includes(this.externalSiteForm.disparador) ||
        this.externalSiteForm.formato === 4
            ) {
                this.status_objective = true;
                this.externalSiteForm.objetivo = null;
            } else if (this.externalSiteForm.disparador === 4 && [1, 0].includes(this.externalSiteForm.metodo)) {
                this.status_objective = false;
                this.externalSiteForm.objetivo = 1;
                this.objectives = [
                    { name: 'Embebido', value: 1 },
                    { name: 'Nueva pestaña', value: 2 }
                ];
            } else if (this.externalSiteForm.disparador === 4 && this.externalSiteForm.metodo === 2) {
                this.status_objective = false;
                this.externalSiteForm.objetivo = null;
                this.objectives = [
                    { name: '-------', value: null },
                    { name: 'Embebido', value: 1 },
                    { name: 'Nueva pestaña', value: 2 }
                ];
            } else {
                this.status_objective = false;
                this.externalSiteForm.objetivo = 1;
            }
        },
        triggerEvent () {
            this.handleObjetiveStatus();
        },
        methodEvent () {
            // Manejamos el objetivo
            this.handleObjetiveStatus();

            // Manejamos el formato
            if ([1, 0].includes(this.externalSiteForm.metodo)) {
                this.status_format = true;
                this.externalSiteForm.formato = null;
            } else {
                this.status_format = false;
                this.externalSiteForm.formato = 1;
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
            if (status === HTTP_STATUS.SUCCESS) {
                this.$router.push({ name: 'supervisor_external_sites' });
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
