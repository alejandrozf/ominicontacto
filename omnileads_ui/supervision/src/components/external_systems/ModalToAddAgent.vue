<template>
  <Dialog
    :visible="showModal"
    :style="{ width: '50vw' }"
    :closable="false"
    :modal="true"
  >
    <template #header>
      <h2 v-if="modalToCreate">
        {{ $t("views.external_system.new_agent_on_system") }}
      </h2>
      <h2 v-else>{{ $t("views.external_system.edit_agent_on_system") }}</h2>
    </template>
    <div class="card">
      <div class="p-fluid p-grid p-formgrid">
        <div class="field p-col-6" v-if="modalToCreate">
          <label
            id="agente"
            :class="{
              'p-error': v$.agenteEnSistemaForm.agente.$invalid && submitted,
            }"
            >{{ $t("models.agent_external_system.agent") }}*</label
          >
          <Dropdown
            v-model="v$.agenteEnSistemaForm.agente.$model"
            :options="agents"
            optionLabel="full_name"
            optionValue="id"
            placeholder="--------"
            :emptyFilterMessage="$t('globals.without_data')"
            :filter="true"
            class="p-mt-2"
            :class="{
              'p-invalid': v$.agenteEnSistemaForm.agente.$invalid && submitted,
            }"
            v-bind:filterPlaceholder="
              $t('globals.find_by', { field: $tc('globals.name') }, 1)
            "
          />
          <small
            v-if="
              (v$.agenteEnSistemaForm.agente.$invalid && submitted) ||
              v$.agenteEnSistemaForm.agente.$pending.$response
            "
            class="p-error"
            >{{
              v$.agenteEnSistemaForm.agente.required.$message.replace(
                "Value",
                $t("models.agent_external_system.agent")
              )
            }}</small
          >
        </div>
        <div class="field" :class="modalToCreate ? 'p-col-6' : 'p-col-12'">
          <label
            id="id_externo_agente"
            :class="{
              'p-error':
                v$.agenteEnSistemaForm.id_externo_agente.$invalid && submitted,
            }"
            >{{ $t("models.agent_external_system.external_id") }}*</label
          >
          <div class="p-inputgroup p-mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-list"></i>
            </span>
            <InputText
              id="id_externo_agente"
              :class="{
                'p-invalid':
                  v$.agenteEnSistemaForm.id_externo_agente.$invalid &&
                  submitted,
              }"
              :placeholder="$t('forms.external_system.enter_name')"
              v-model="v$.agenteEnSistemaForm.id_externo_agente.$model"
            />
          </div>
          <small
            v-if="
              (v$.agenteEnSistemaForm.id_externo_agente.$invalid &&
                submitted) ||
              v$.agenteEnSistemaForm.id_externo_agente.$pending.$response
            "
            class="p-error"
            >{{
              v$.agenteEnSistemaForm.id_externo_agente.required.$message.replace(
                "Value",
                $t("models.agent_external_system.external_id")
              )
            }}</small
          >
        </div>
      </div>
      <div class="p-flex p-justify-content-end p-flex-wrap">
        <Button
          class="p-button-danger p-button-outlined p-mr-2"
          :label="$t('globals.cancel')"
          @click="closeModal"
        />
        <Button
          :label="$t('globals.save')"
          class="p-mt-4"
          @click="save(!v$.$invalid)"
        />
      </div>
    </div>
  </Dialog>
</template>

<script>
import { mapActions } from 'vuex';
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';

export default {
    setup: () => ({ v$: useVuelidate({ $scope: false }) }),
    validations () {
        return {
            agenteEnSistemaForm: {
                id_externo_agente: { required },
                agente: { required }
            }
        };
    },
    props: {
        modalToCreate: {
            type: Boolean,
            default: true
        },
        showModal: {
            type: Boolean,
            default: false
        },
        agents: {
            type: Object,
            default: () => {}
        },
        agenteEnSistema: {
            type: Object,
            default () {
                return {
                    id_externo_agente: '',
                    agente: -1
                };
            }
        }
    },
    data () {
        return {
            submitted: false,
            agenteEnSistemaForm: {
                id_externo_agente: '',
                agente: -1
            }
        };
    },
    created () {
        this.initModalData();
    },
    methods: {
        ...mapActions(['']),
        initModalData () {
            this.submitted = false;
            this.agenteEnSistemaForm = {
                id_externo_agente: '',
                agente: -1
            };
        },
        initAgent () {
            this.agenteEnSistemaForm.id_externo_agente =
        this.agenteEnSistema.id_externo_agente;
            this.agenteEnSistemaForm.agente = this.agenteEnSistema.agente;
        },
        closeModal () {
            this.initModalData();
            this.$emit('handleModalEvent', { showModal: false, modalToCreate: true });
        },
        save (isFormValid) {
            this.submitted = true;
            if (!isFormValid) {
                return null;
            }
            if (this.modalToCreate) {
                this.$emit('addAgentEvent', this.agenteEnSistemaForm);
            } else {
                this.$emit('editAgentEvent', this.agenteEnSistemaForm);
            }
            this.closeModal();
        }
    },
    watch: {
        agents: {
            handler () {},
            deep: true,
            immediate: true
        },
        agenteEnSistema: {
            handler () {
                this.initAgent();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
