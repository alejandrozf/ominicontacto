<template>
  <div class="card">
    <DataTable
      :value="destinationOptions"
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
      filterDisplay="menu"
      :globalFilterFields="['dtmf']"
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
                  $t('globals.find_by', { field: $t('models.destination_option.dtmf') })
                "
              />
            </span>
            <Button
              type="button"
              icon="pi pi-plus"
              class="p-button-info ml-2"
              @click="newDestinationOption"
            />
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="dtmf"
        :header="$t('models.destination_option.dtmf')"
      ></Column>
      <Column
        field="destination_type"
        :header="$t('models.destination_option.destination_type')"
      >
        <template #body="slotProps">
          {{ getDestinationType(slotProps.data.destination_type) }}
        </template>
      </Column>
      <Column
        field="destination"
        :header="$t('models.destination_option.destination')"
      >
        <template #body="slotProps">
          {{ getDestination(slotProps.data.destination_type, slotProps.data.destination) }}
        </template>
      </Column>
      <Column
        :header="$tc('globals.option', 2)"
        style="max-width: 25rem"
        :exportable="false"
      >
        <template #body="slotProps">
          <Button
            icon="pi pi-pencil"
            class="p-button-warning ml-2"
            @click="editDestinationOption(slotProps.data)"
            v-tooltip.top="$t('globals.edit')"
          />
          <Button
            v-if='destinationOptions.length > 1'
            icon="pi pi-trash"
            class="p-button-danger ml-2"
            @click="removeDestinationOption(slotProps.data)"
            v-tooltip.top="$t('globals.delete')"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { FilterMatchMode } from 'primevue/api';
import {
    CAMPAIGN,
    VALIDATION_DATE,
    IVR,
    HANGUP,
    ID_CLIENT,
    CUSTOM_DST,
    AGENT
} from '@/globals/supervisor/ivr';

export default {
    inject: ['$helpers'],
    props: {
        destinationOptions: {
            type: Array,
            default: () => []
        }
    },
    data () {
        return {
            filters: null,
            destination_types: [
                {
                    option: this.$t('forms.ivr.destination_types.campaign'),
                    value: CAMPAIGN
                },
                {
                    option: this.$t('forms.ivr.destination_types.validation_date'),
                    value: VALIDATION_DATE
                },
                {
                    option: this.$t('forms.ivr.destination_types.ivr'),
                    value: IVR
                },
                {
                    option: this.$t('forms.ivr.destination_types.hangup'),
                    value: HANGUP
                },
                {
                    option: this.$t('forms.ivr.destination_types.id_client'),
                    value: ID_CLIENT
                },
                {
                    option: this.$t('forms.ivr.destination_types.custom_dst'),
                    value: CUSTOM_DST
                },
                {
                    option: this.$t('forms.ivr.destination_types.agent'),
                    value: AGENT
                }
            ]
        };
    },
    created () {
        this.initFilters();
    },
    computed: {
        ...mapState(['ivrDestinations'])
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
        newDestinationOption () {
            this.$emit('handleDestinationOptionModalEvent', {
                showModal: true, formToCreate: true, destinationOption: null
            });
        },
        editDestinationOption (destinationOption) {
            this.$emit('handleDestinationOptionModalEvent', {
                showModal: true, formToCreate: false, destinationOption
            });
        },
        getDestinationType (type) {
            return type !== null ? this.destination_types.find(d => d.value === type).option : '------';
        },
        getDestination (type, destination) {
            if (this.ivrDestinations.length > 0 || this.ivrDestinations !== null) {
                return destination !== null ? this.ivrDestinations[`${type}`].find(d => d.id === destination).nombre : '------';
            }
            return '------';
        },
        ...mapActions(['removeDestinationOption'])
    },
    watch: {
        destinationOptions: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
