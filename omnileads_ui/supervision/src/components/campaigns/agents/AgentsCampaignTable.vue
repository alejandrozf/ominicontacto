<template>
  <div class="card">
    <!-- eslint-disable vue/no-v-model-argument -->
    <DataTable
      :value="agents_by_campaign"
      class="p-datatable-sm editable-cells-table"
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
      v-model:filters="filters"
      filterDisplay="menu"
      :globalFilterFields="[
        'agent_full_name',
        'agent_penalty',
        'representative.name',
      ]"
      editMode="cell"
    >
      <template #header>
        <div class="flex justify-content-between flex-wrap">
          <div class="flex align-items-center justify-content-center">
            <Button
              type="button"
              icon="pi pi-filter-slash"
              :label="$t('globals.clean_filter')"
              class="p-button-outlined"
              @click="clearFilter()"
            />
          </div>
          <div class="flex align-items-center justify-content-center">
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText
                v-model="filters['global'].value"
                icon="pi pi-check"
                :placeholder="
                  $t('globals.find_by', { field: $tc('globals.name', 1) })
                "
              />
            </span>
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="agent_full_name"
        :header="$t('models.agent_campaign.name')"
      ></Column>
      <Column
        field="agent_username"
        :header="$t('models.agent_campaign.username')"
      ></Column>
      <Column
        field="agent_sip_id"
        :header="$t('models.agent_campaign.sip')"
        :sortable="true"
      ></Column>
      <Column
        field="agent_penalty"
        :header="$t('models.agent_campaign.penalty')"
        :sortable="true"
      >
        <template #editor="{ data, field }">
          <Dropdown
            v-model="data[field]"
            :options="penalties"
            @change="changePenalty(data)"
            optionLabel="label"
            optionValue="value"
            :placeholder="
              $t('globals.select_type', { type: $t('globals.penalty') }, 2)
            "
          >
            <template #option="slotProps">
              <span>{{ slotProps.option.label }}</span>
            </template>
          </Dropdown>
        </template>
      </Column>
      <Column :header="$tc('globals.option')" :exportable="false">
        <template #body="slotProps">
          <Button
            icon="pi pi-trash"
            class="p-button-danger"
            @click="removeAgent(slotProps.data.agent_id)"
            v-tooltip.top="$t('globals.delete')"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import { FilterMatchMode } from 'primevue/api';

export default {
    inject: ['$helpers'],
    data () {
        return {
            filters: null,
            penalties: [
                { label: `${this.$t('globals.penalty')} 0`, value: 0 },
                { label: `${this.$t('globals.penalty')} 1`, value: 1 },
                { label: `${this.$t('globals.penalty')} 2`, value: 2 },
                { label: `${this.$t('globals.penalty')} 3`, value: 3 },
                { label: `${this.$t('globals.penalty')} 4`, value: 4 },
                { label: `${this.$t('globals.penalty')} 5`, value: 5 },
                { label: `${this.$t('globals.penalty')} 6`, value: 6 },
                { label: `${this.$t('globals.penalty')} 7`, value: 7 },
                { label: `${this.$t('globals.penalty')} 8`, value: 8 },
                { label: `${this.$t('globals.penalty')} 9`, value: 9 }
            ]
        };
    },
    created () {
        this.initFilters();
    },
    methods: {
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        removeAgent (agentId) {
            this.removeAgentOfCampaign(agentId);
            this.$swal(
                this.$helpers.getToasConfig(
                    this.$t('globals.success_notification'),
                    this.$tc('globals.success_deleted_type', {
                        type: this.$tc('globals.agent')
                    }),
                    this.$t('globals.icon_success'),
                    this.$t('views.add_agents_to_campaign.how_to_update')
                )
            );
        },
        changePenalty (data) {
            this.updateAgentPenalty({
                agent_id: data.agent_id,
                penalty: data.agent_penalty
            });
            this.$swal(
                this.$helpers.getToasConfig(
                    this.$t('globals.success_notification'),
                    this.$tc('globals.success_updated_type', {
                        type: this.$t('globals.penalty')
                    }),
                    this.$t('globals.icon_success'),
                    this.$t('views.add_agents_to_campaign.how_to_update')
                )
            );
        },
        ...mapActions(['removeAgentOfCampaign', 'updateAgentPenalty'])
    },
    watch: {
        agents_by_campaign: {
            deep: true,
            handler () {}
        }
    },
    computed: {
        ...mapGetters({
            agents_by_campaign: 'getAgentsByCampaign'
        })
    }
};
</script>
