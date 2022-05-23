<template>
  <!-- eslint-disable vue/no-v-model-argument -->
  <DataTable
    :value="tableData"
    ref="dt"
    :paginator="true"
    class="p-datatable-customers"
    showGridlines
    :scrollable="true"
    scrollHeight="600px"
    :rows="10"
    :rowsPerPageOptions="[10, 20, 50]"
    paginatorTemplate="CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
    :currentPageReportTemplate="
      $t('globals.showing_datatable_info', {
        first: '{first}',
        last: '{last}',
        totalRecords: '{totalRecords}',
      })
    "
    dataKey="id"
    :filters="filters"
    filterDisplay="menu"
    :loading="loading"
    stripedRows
    responsiveLayout="scroll"
    :globalFilterFields="['actor', 'object', 'name', 'action', 'date']"
  >
    <template #header>
      <div class="p-d-flex p-jc-between">
        <Button
          icon="pi pi-external-link"
          class="p-button-info"
          :label="$t('globals.export_type', { type: 'CSV' })"
          @click="exportCSV($event)"
        />
        <div>
          <Button
            type="button"
            icon="pi pi-filter-slash"
            :label="$t('globals.clean_filter')"
            class="p-button-outlined p-mr-2"
            @click="clearFilter()"
          />
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText
              v-model="filters['global'].value"
              icon="pi pi-check"
              :placeholder="$tc('globals.find', 2)"
            />
          </span>
        </div>
      </div>
    </template>
    <template #empty> {{ $t("globals.without_data") }} </template>
    <template #loading> {{ $t("globals.load_info") }} </template>
    <Column
      field="actor"
      :header="$tc('models.audit.user')"
      :sortable="true"
    ></Column>
    <Column
      field="object"
      :header="$tc('models.audit.object')"
      :sortable="true"
    ></Column>
    <Column
      field="name"
      :header="$tc('models.audit.name')"
      :sortable="true"
    ></Column>
    <Column
      field="action"
      :header="$tc('models.audit.action')"
      :sortable="true"
    ></Column>
    <Column field="changes" :header="$tc('models.audit.change')"></Column>
    <Column
      field="date"
      :header="$tc('models.audit.datetime')"
      :sortable="true"
    ></Column>
  </DataTable>
</template>
<script>
import { FilterMatchMode, FilterOperator } from 'primevue/api';
import { ref } from 'vue';

export default {
    props: {
        tableData: Object,
        loading: Boolean
    },
    setup () {
        const filters = ref({
            global: { value: null, matchMode: FilterMatchMode.CONTAINS },
            actor: {
                operator: FilterOperator.AND,
                constraints: [{ value: null, matchMode: FilterMatchMode.EQUALS }]
            },
            action: {
                operator: FilterOperator.AND,
                constraints: [{ value: null, matchMode: FilterMatchMode.EQUALS }]
            },
            date: {
                operator: FilterOperator.AND,
                constraints: [{ value: null, matchMode: FilterMatchMode.DATE_IS }]
            }
        });

        const dates = ref();
        const dt = ref();

        const clearFilter = () => {
            initFilters();
        };
        const initFilters = () => {
            filters.value = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS },
                actor: {
                    operator: FilterOperator.AND,
                    constraints: [{ value: null, matchMode: FilterMatchMode.EQUALS }]
                },
                action: {
                    operator: FilterOperator.AND,
                    constraints: [{ value: null, matchMode: FilterMatchMode.EQUALS }]
                },
                date: {
                    operator: FilterOperator.AND,
                    constraints: [{ value: null, matchMode: FilterMatchMode.DATE_IS }]
                }
            };
        };
        const exportCSV = () => {
            dt.value.exportCSV();
        };

        return { dates, filters, clearFilter, initFilters, dt, exportCSV };
    }
};
</script>
