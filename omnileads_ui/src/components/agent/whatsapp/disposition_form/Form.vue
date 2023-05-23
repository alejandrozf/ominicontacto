<template>
  <div class="card">
    <div class="grid formgrid mt-1">
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          id="disposition_form_tipo"
          :class="{
            'p-error': v$.form.tipo.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.disposition_form.type") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <Dropdown
            id="disposition_form_tipo"
            v-model="v$.form.tipo.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.form.tipo.$invalid && submitted,
            }"
            :options="tipos"
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
            (v$.form.tipo.$invalid && submitted) ||
            v$.form.tipo.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.form.tipo.required.$message.replace(
              "Value",
              $t("models.whatsapp.disposition_form.type")
            )
          }}
        </small>
      </div>
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          id="disposition_form_resultado"
          :class="{
            'p-error': v$.form.resultado.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.disposition_form.result") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <Dropdown
            id="disposition_form_resultado"
            v-model="v$.form.resultado.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.form.resultado.$invalid && submitted,
            }"
            :options="resultados"
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
            (v$.form.resultado.$invalid && submitted) ||
            v$.form.resultado.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.form.resultado.required.$message.replace(
              "Value",
              $t("models.whatsapp.disposition_form.result")
            )
          }}
        </small>
      </div>
    </div>
    <div class="grid formgrid mt-1">
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          id="disposition_form_medio"
          :class="{
            'p-error': v$.form.medio.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.disposition_form.mean") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <Dropdown
            id="disposition_form_medio"
            v-model="v$.form.medio.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.form.medio.$invalid && submitted,
            }"
            :options="medios"
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
            (v$.form.medio.$invalid && submitted) ||
            v$.form.medio.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.form.medio.required.$message.replace(
              "Value",
              $t("models.whatsapp.disposition_form.mean")
            )
          }}
        </small>
      </div>
      <div class="field sm:col-12 md:col-12 lg:col-6 xl:col-6">
        <label
          id="disposition_form_calificacion"
          :class="{
            'p-error': v$.form.calificacion.$invalid && submitted,
          }"
          >{{ $t("models.whatsapp.disposition_form.score") }}*</label
        >
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <Dropdown
            id="disposition_form_calificacion"
            v-model="v$.form.calificacion.$model"
            class="w-full"
            :class="{
              'p-invalid': v$.form.calificacion.$invalid && submitted,
            }"
            :options="calificaciones"
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
            (v$.form.calificacion.$invalid && submitted) ||
            v$.form.calificacion.$pending.$response
          "
          class="p-error"
        >
          {{
            v$.form.calificacion.required.$message.replace(
              "Value",
              $t("models.whatsapp.disposition_form.score")
            )
          }}
        </small>
      </div>
    </div>
    <div class="grid formgrid mt-1">
      <div class="field sm:col-12 md:col-12 lg:col-12 xl:col-12">
        <label id="disposition_form_observaciones">{{
          $t("models.whatsapp.disposition_form.observation")
        }}</label>
        <div class="p-inputgroup mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-eye"></i>
          </span>
          <Textarea v-model="form.observaciones" rows="10" cols="30" />
        </div>
      </div>
    </div>
    <div class="flex justify-content-end flex-wrap mt-2">
      <div class="flex align-items-center">
        <Button
          class="p-button-danger p-button-outlined mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal"
        />
        <Button
          :label="$t('globals.save')"
          icon="pi pi-save"
          @click="save(!v$.$invalid)"
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
import {
    RESULTS,
    TYPES,
    SCORES,
    MEANS
} from '@/globals/agent/whatsapp/disposition';
import { HTTP_STATUS } from '@/globals';
import { notificationEvent } from '@/globals/agent/whatsapp';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                tipo: { required },
                medio: { required },
                resultado: { required },
                calificacion: { required }
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
            form: {
                id: null,
                tipo: null,
                medio: null,
                resultado: null,
                calificacion: null,
                observaciones: null
            },
            submitted: false,
            filters: null,
            tipos: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.provider.types.twilio'),
                    value: TYPES.OPT1
                }
            ],
            medios: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.provider.types.twilio'),
                    value: MEANS.OPT1
                }
            ],
            resultados: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.provider.types.twilio'),
                    value: RESULTS.OPT1
                }
            ],
            calificaciones: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.provider.types.twilio'),
                    value: SCORES.OPT1
                }
            ]
        };
    },
    created () {
        this.initializeData();
    },
    computed: {
        ...mapState(['agtWhatsManagementForm'])
    },
    methods: {
        ...mapActions(['agtWhatsManagementCreate', 'agtWhatsManagementInitData']),
        resetData () {
            this.form = {
                id: null,
                tipo: null,
                medio: null,
                resultado: null,
                calificacion: null,
                observaciones: null
            };
            this.submitted = false;
        },
        closeModal () {
            this.resetData();
            this.$emit('clearForm');
            const event = new CustomEvent('onWhatsappDispositionFormEvent', {
                detail: {
                    disposition_form: false
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        initFormData () {
            this.form.id = this.agtWhatsManagementForm?.id;
            this.form.tipo = this.agtWhatsManagementForm?.tipo;
            this.form.medio = this.agtWhatsManagementForm?.medio;
            this.form.resultado = this.agtWhatsManagementForm?.resultado;
            this.form.calificacion = this.agtWhatsManagementForm?.calificacion;
            this.form.observaciones = this.agtWhatsManagementForm?.observaciones;
        },
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        async save (isFormValid) {
            try {
                this.submitted = true;
                if (!isFormValid) {
                    return null;
                }
                var response = null;
                if (this.formToCreate) {
                    response = await this.agtWhatsManagementCreate(this.form);
                }
                const { status, message } = response;
                this.closeModal();
                if (status === HTTP_STATUS.SUCCESS) {
                    await this.agtWhatsManagementInitData();
                    await notificationEvent(
                        this.$t('globals.success_notification'),
                        message,
                        this.$t('globals.icon_success')
                    );
                } else {
                    await notificationEvent(
                        this.$t('globals.error_notification'),
                        message,
                        this.$t('globals.icon_error')
                    );
                }
            } catch (error) {
                console.error('ERROR Al calificar conversacion');
                console.error(error);
                await notificationEvent(
                    this.$t('globals.error_notification'),
                    'Error al calificar conversacion',
                    this.$t('globals.icon_error')
                );
            }
        }
    },
    watch: {
        agtWhatsManagementForm: {
            handler () {
                if (this.agtWhatsManagementForm) {
                    this.initFormData();
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
