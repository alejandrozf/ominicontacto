<template>
    <DataTable :value="tableData" ref="dt"  :paginator="true" class="p-datatable-customers" showGridlines :rows="10"
        dataKey="id" v-model:filters="filters" filterDisplay="menu" :loading="loading" stripedRows responsiveLayout="scroll"
        :globalFilterFields="['actor', 'object', 'name', 'action','date']">
    <template #header>
            <div class="p-grid">
                <div class="p-field p-col-3">
                    <Button icon="pi pi-external-link" label="Export CSV" @click="exportCSV($event)" />
                </div>
                <div class="p-field p-col-6 p-lg-offset-3">
                    <span class="p-float-label p-input-icon-left">
                        <i class="pi pi-search" />
                        <InputText id="inputtext-left" type="text" v-model="filters['global'].value" />
                        <label for="inputtext-left">Filtros </label>
                    </span>
                     <Button type="button" icon="pi pi-filter-slash" label="Clear" class="p-button-secondary" @click="clearFilter()"/>
                </div>
            </div>
    </template>
    <template #empty>
                No data found.
    </template>
    <template #loading>
                Loading option data. Please wait.
    </template>
    <Column field="actor" header="Usuario" :sortable="true"></Column>
    <Column field="object" header="Objeto" :sortable="true"></Column>
    <Column field="name" header="Nombre" :sortable="true"></Column>
    <Column field="action" header="Acción" :sortable="true"></Column>
    <Column field="changes" header="Cambio"></Column>
    <Column field="date" header="DateTime" :sortable="true"></Column>
    </DataTable>
</template>
<script>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import {FilterMatchMode,FilterOperator} from 'primevue/api';
import InputText from 'primevue/inputtext';
import { ref } from 'vue';

export default {
    props: { 
        tableData: Object,
        loading: Boolean, 
    },
    components: {
        DataTable,
        Column,
        InputText
    },
    setup() {
        const filters = ref({
            'global': {value: null, matchMode: FilterMatchMode.CONTAINS},
            'actor': {operator: FilterOperator.AND, constraints: [{value: null, matchMode: FilterMatchMode.EQUALS}]},
            'action': {operator: FilterOperator.AND, constraints: [{value: null, matchMode: FilterMatchMode.EQUALS}]},
            'date': {operator: FilterOperator.AND, constraints: [{value: null, matchMode: FilterMatchMode.DATE_IS}]},
        });

        const dates = ref();
        const dt = ref();

        const clearFilter = () => {
            initFilters();
        };
        const initFilters = () => {
            filters.value = {
                'global': {value: null, matchMode: FilterMatchMode.CONTAINS},
                'actor': {operator: FilterOperator.AND, constraints: [{value: null, matchMode: FilterMatchMode.EQUALS}]},
                'action': {operator: FilterOperator.AND, constraints: [{value: null, matchMode: FilterMatchMode.EQUALS}]},
                'date': {operator: FilterOperator.AND, constraints: [{value: null, matchMode: FilterMatchMode.DATE_IS}]},
            }
        };
        const exportCSV = () => {
            dt.value.exportCSV();
        };

        return {dates, filters, clearFilter, initFilters, dt, exportCSV}
    }
}
</script>

