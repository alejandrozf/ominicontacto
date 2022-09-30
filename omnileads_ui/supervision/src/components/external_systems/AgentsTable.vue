<template>
  <div class="card">
    <h3>{{ $tc("globals.agent", 2) }}</h3>
    <DataTable
      :value="agents"
      class="p-datatable-sm"
      showGridlines
      :scrollable="true"
      scrollHeight="600px"
      responsiveLayout="scroll"
      dataKey="id"
      :rows="10"
      :rowsPerPageOptions="[10, 20, 50]"
      :paginator="true"
      paginatorTemplate="CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
      :currentPageReportTemplate="
        $t('globals.showing_datatable_info', {
          first: '{first}',
          last: '{last}',
          totalRecords: '{totalRecords}',
        })
      "
      :filters="filters"
      :globalFilterFields="['id_externo_agente']"
    >
      <template #header>
        <div class="flex justify-content-between flex-wrap">
          <div class="flex align-items-center justify-content-center">
            <Button
              type="button"
              icon="pi pi-filter-slash"
              :label="$t('globals.clean_filter')"
              class="p-button-outlined"
              @click="clearFilter"
            />
          </div>
          <div class="flex align-items-center justify-content-center">
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText
                v-model="filters['global'].value"
                icon="pi pi-check"
                :placeholder="
                  $t('globals.find_by', {
                    field: $tc('models.agent_external_system.external_id', 1),
                  })
                "
              />
            </span>
            <Button
              v-if="!tableToShow"
              type="button"
              icon="pi pi-plus"
              :label="$t('globals.new')"
              class="ml-2"
              @click="addAgentOnSystem"
            />
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="agente"
        :sortable="true"
        :header="$t('models.agent_external_system.agent')"
      >
        <template #body="slotProps">
          {{ getAgentInfo(slotProps.data.agente) }}
        </template>
      </Column>
      <Column
        field="id_externo_agente"
        :sortable="true"
        :header="$t('models.agent_external_system.external_id')"
      ></Column>
      <Column
        v-if="!tableToShow"
        :header="$tc('globals.option', 2)"
        style="max-width: 25rem"
        :exportable="false"
      >
        <template #body="slotProps">
          <Button
            icon="pi pi-pencil"
            class="p-button-warning ml-2"
            @click="edit(slotProps.data)"
            v-tooltip.top="$t('globals.edit')"
          />
          <Button
            icon="pi pi-trash"
            class="p-button-danger ml-2"
            @click="remove(slotProps.data)"
            v-tooltip.top="$t('globals.delete')"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script>
import { FilterMatchMode } from 'primevue/api';
import { mapActions, mapState } from 'vuex';

export default {
    inject: ['$helpers'],
    props: {
        tableToShow: {
            type: Boolean,
            default: false
        },
        agents: {
            type: Array,
            default: () => []
        }
    },
    data () {
        return {
            filters: null
        };
    },
    async created () {
        await this.initializeData();
        await this.initAgentsExternalSystems();
    },
    methods: {
        ...mapActions(['initAgentsExternalSystems']),
        initializeData () {
            this.initFilters();
        },
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        addAgentOnSystem () {
            this.$emit('handleModalEvent', { showModal: true, modalToCreate: true });
        },
        getAgentInfo (id) {
            var agent = null;
            if (this.agents.length > 0) {
                agent = this.agentsExternalSystem.find((a) => a.id === id);
            }
            return agent ? agent.full_name : '';
        },
        edit (agenteEnSistema) {
            this.$emit('editAgentEvent', agenteEnSistema);
        },
        remove (agenteEnSistema) {
            this.$emit('removeAgentEvent', agenteEnSistema);
        }
    },
    computed: {
        ...mapState(['agentsExternalSystem'])
    },
    watch: {
        agents: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
