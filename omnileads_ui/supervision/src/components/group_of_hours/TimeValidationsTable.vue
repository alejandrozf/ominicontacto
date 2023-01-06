<template>
  <div class="card">
    <DataTable
      :value="timeValidations"
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
      :globalFilterFields="['match_pattern']"
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
            <Button
              v-if="showOptions"
              type="button"
              icon="pi pi-plus"
              class="p-button-info ml-2"
              @click="newTimeValidation"
            />
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="tiempo_inicial"
        :header="$t('models.time_validation.tiempo_inicial')"
      ></Column>
      <Column
        field="tiempo_final"
        :header="$t('models.time_validation.tiempo_final')"
      ></Column>
      <Column
        field="dia_semana_inicial"
        :header="$t('models.time_validation.dia_semana_inicial')"
      >
        <template #body="slotProps">
          {{ getDiaDeLaSemana(slotProps.data.dia_semana_inicial) }}
        </template>
      </Column>
      <Column
        field="dia_semana_final"
        :header="$t('models.time_validation.dia_semana_final')"
      >
        <template #body="slotProps">
          {{ getDiaDeLaSemana(slotProps.data.dia_semana_final) }}
        </template>
      </Column>
      <Column
        field="dia_mes_inicio"
        :header="$t('models.time_validation.dia_mes_inicio')"
      >
        <template #body="slotProps">
          {{ getDiaDelMes(slotProps.data.dia_mes_inicio) }}
        </template>
      </Column>
      <Column
        field="dia_mes_final"
        :header="$t('models.time_validation.dia_mes_final')"
      >
        <template #body="slotProps">
          {{ getDiaDelMes(slotProps.data.dia_mes_final) }}
        </template>
      </Column>
      <Column
        field="mes_inicio"
        :header="$t('models.time_validation.mes_inicio')"
      >
        <template #body="slotProps">
          {{ getMes(slotProps.data.mes_inicio) }}
        </template>
      </Column>
      <Column
        field="mes_final"
        :header="$t('models.time_validation.mes_final')"
      >
        <template #body="slotProps">
          {{ getMes(slotProps.data.mes_final) }}
        </template>
      </Column>
      <Column
        v-if="showOptions"
        :header="$tc('globals.option', 2)"
        style="max-width: 25rem"
        :exportable="false"
      >
        <template #body="slotProps">
          <Button
            icon="pi pi-pencil"
            class="p-button-warning ml-2"
            @click="editTimeValidation(slotProps.data)"
            v-tooltip.top="$t('globals.edit')"
          />
          <Button
            v-if='timeValidations.length > 1'
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
import { mapActions, mapState } from 'vuex';
import { FilterMatchMode } from 'primevue/api';

export default {
    inject: ['$helpers'],
    props: {
        timeValidations: {
            type: Array,
            default: () => []
        },
        showOptions: {
            type: Boolean,
            default: true
        }
    },
    data () {
        return {
            filters: null
        };
    },
    created () {
        this.initFilters();
    },
    computed: {
        ...mapState(['weekdays', 'months'])
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
        newTimeValidation () {
            this.$emit('handleTimeValidationModalEvent', true, true, null);
        },
        editTimeValidation (timeValidation) {
            this.$emit('handleTimeValidationModalEvent', true, false, timeValidation);
        },
        remove (timeValidation) {
            this.removeTimeValidation(timeValidation);
        },
        getDiaDeLaSemana (dia) {
            return dia !== null ? this.weekdays.find(d => d.value === dia).option : '------';
        },
        getDiaDelMes (dia) {
            return dia !== null ? dia : '------';
        },
        getMes (mes) {
            return mes !== null ? this.months.find(m => m.value === mes).option : '------';
        },
        ...mapActions(['removeTimeValidation'])
    },
    watch: {
        timeValidations: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
