<template>
  <div class="card">
    <div class="p-fluid p-grid p-formgrid p-mt-4">
      <div class="field p-col-12">
        <label
          id="external_system_name"
          :class="{
            'p-error': v$.externalSystemForm.nombre.$invalid && submitted,
          }"
          >{{ $t("models.external_system.name") }}*</label
        >
        <div class="p-inputgroup p-mt-2">
          <span class="p-inputgroup-addon">
            <i class="pi pi-list"></i>
          </span>
          <InputText
            id="external_system_name"
            :class="{
              'p-invalid': v$.externalSystemForm.nombre.$invalid && submitted,
            }"
            :placeholder="$t('forms.external_system.enter_name')"
            v-model="v$.externalSystemForm.nombre.$model"
          />
        </div>
        <small
          v-if="
            (v$.externalSystemForm.nombre.$invalid && submitted) ||
            v$.externalSystemForm.nombre.$pending.$response
          "
          class="p-error"
          >{{
            v$.externalSystemForm.nombre.required.$message.replace(
              "Value",
              $t("models.external_system.name")
            )
          }}</small
        >
      </div>
    </div>
    <AgentsTable
      :agents="externalSystemForm.agentes"
      @handleModalEvent="handleModal"
      @removeAgentEvent="removeAgentOnSystem"
      @editAgentEvent="modalToEditAgentOnSystem"
    />
    <div class="p-flex p-flex-row-reverse p-flex-wrap">
      <div class="p-flex p-align-items-center">
        <Button
          :label="$t('globals.save')"
          icon="pi pi-save"
          class="p-mt-4"
          @click="saveExternalSystem(!v$.$invalid)"
        />
      </div>
    </div>
    <ModalToAddAgent
      :showModal="showModal"
      :modalToCreate="modalToCreate"
      :agents="agentsFilter"
      :agenteEnSistema="agenteEnSistema"
      @handleModalEvent="handleModal"
      @addAgentEvent="addAgentOnSystem"
      @editAgentEvent="editAgentOnSystem"
    />
  </div>
</template>

<script>
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import { mapActions, mapState } from 'vuex';
import AgentsTable from '@/components/external_systems/AgentsTable';
import ModalToAddAgent from '@/components/external_systems/ModalToAddAgent';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            externalSystemForm: {
                nombre: { required }
            }
        };
    },
    inject: ['$helpers'],
    props: {
        formToCreate: {
            type: Boolean,
            default: true
        },
        externalSystem: {
            type: Object,
            default () {
                return {
                    nombre: '',
                    agentes: []
                };
            }
        }
    },
    components: {
        AgentsTable,
        ModalToAddAgent
    },
    data () {
        return {
            externalSystemForm: {
                nombre: '',
                agentes: []
            },
            agenteEnSistema: {
                id_externo_agente: '',
                agente: -1
            },
            agentsFilter: [],
            showModal: false,
            submitted: false,
            modalToCreate: true
        };
    },
    computed: {
        ...mapState(['agentsExternalSystem'])
    },
    async created () {
        await this.initializeData();
        await this.initAgentsExternalSystems();
        await this.filterAgents();
    },
    methods: {
        ...mapActions([
            'createExternalSystem',
            'updateExternalSystem',
            'initAgentsExternalSystems'
        ]),
        initializeData () {
            this.initFormData();
        },
        initFormData () {
            this.externalSystemForm.nombre = this.externalSystem.nombre;
            this.externalSystemForm.agentes = this.externalSystem.agentes;
            this.submitted = false;
        },
        handleModal ({ showModal, modalToCreate }) {
            this.showModal = showModal;
            this.modalToCreate = modalToCreate;
        },
        filterAgents () {
            if (this.externalSystemForm.agentes.length > 0) {
                var agentIds = this.externalSystemForm.agentes.map((a) => a.agente);
                this.agentsFilter = this.agentsExternalSystem.filter(
                    (a) => !agentIds.includes(a.id)
                );
            } else {
                this.agentsFilter = this.agentsExternalSystem;
            }
        },
        addAgentOnSystem (data) {
            this.externalSystemForm.agentes.push(data);
            this.filterAgents();
        },
        removeAgentOnSystem (data) {
            this.externalSystemForm.agentes = this.externalSystemForm.agentes.filter(
                (a) => a.agente !== data.agente
            );
            this.filterAgents();
        },
        editAgentOnSystem (data) {
            this.externalSystemForm.agentes.find(function (a) {
                if (a.agente === data.agente) {
                    a.id_externo_agente = data.id_externo_agente;
                }
            });
        },
        modalToEditAgentOnSystem (data) {
            this.agenteEnSistema = data;
            this.showModal = true;
            this.modalToCreate = false;
        },
        async saveExternalSystem (isFormValid) {
            this.submitted = true;
            if (!isFormValid) {
                return null;
            }
            var response = null;
            var successMsg = null;
            var errorMsg = null;
            if (this.formToCreate) {
                response = await this.createExternalSystem(this.externalSystemForm);
                successMsg = this.$tc('globals.success_added_type', {
                    type: this.$tc('globals.external_system')
                });
                errorMsg = this.$tc('globals.error_to_created_type', {
                    type: this.$tc('globals.external_system')
                });
            } else {
                response = await this.updateExternalSystem({
                    id: this.externalSystem.id,
                    data: this.externalSystemForm
                });
                successMsg = this.$tc('globals.success_updated_type', {
                    type: this.$tc('globals.external_system')
                });
                errorMsg = this.$tc('globals.error_to_updated_type', {
                    type: this.$tc('globals.external_system')
                });
            }
            if (response) {
                this.$router.push({ name: 'external_systems' });
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        successMsg,
                        this.$t('globals.icon_success')
                    )
                );
            } else {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        errorMsg,
                        this.$t('globals.icon_error')
                    )
                );
            }
        }
    },
    watch: {
        externalSystem: {
            handler () {
                this.initFormData();
                this.filterAgents();
            },
            deep: true,
            immediate: true
        },
        formToCreate: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
