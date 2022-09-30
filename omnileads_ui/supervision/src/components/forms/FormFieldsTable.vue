<template>
  <div class="card">
    <DataTable
      :value="fields"
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
      :globalFilterFields="['nombre_campo']"
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
              type="button"
              icon="pi pi-plus"
              :label="$t('globals.new')"
              class="ml-2"
              @click="addFieldToForm"
            />
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column field="orden" :header="$t('models.form_field.order')"></Column>
      <Column
        field="nombre_campo"
        :sortable="true"
        :header="$t('models.form_field.name')"
      ></Column>
      <Column
        field="tipo"
        :sortable="true"
        :header="$t('models.form_field.type')"
      >
        <template #body="slotProps">
          {{ getType(slotProps.data.tipo) }}
        </template>
      </Column>
      <Column
        :header="$t('models.form_field.required')"
        dataType="boolean"
        field="is_required"
        :sortable="true"
      >
        <template #body="{ data }">
          <i
            v-if="data.is_required"
            class="pi pi-check-circle"
            style="color: green"
          ></i>
          <i v-else class="pi pi-times-circle" style="color: red"></i>
        </template>
      </Column>
      <Column
        field="values_select"
        :header="$t('models.form_field.list_options')"
      >
        <template #body="slotProps">
          {{
            slotProps.data.values_select
              ? slotProps.data.values_select
              : "------"
          }}
        </template>
      </Column>
      <Column
        :header="$tc('globals.option', 2)"
        style="max-width: 25rem"
        :exportable="false"
      >
        <template #body="slotProps">
          <Button
            icon="pi pi-trash"
            class="p-button-danger"
            @click="remove(slotProps.data)"
            v-tooltip.top="$t('globals.delete')"
          />
          <Button
            v-if="slotProps.data.orden > 1"
            icon="pi pi-angle-up"
            class="p-button-info ml-2"
            @click="up(slotProps.data)"
            v-tooltip.top="$t('globals.up')"
          />
          <Button
            v-if="fields.length > slotProps.data.orden"
            icon="pi pi-angle-down"
            class="p-button-secondary ml-2"
            @click="down(slotProps.data)"
            v-tooltip.top="$t('globals.down')"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script>
import { FilterMatchMode } from 'primevue/api';

export default {
    inject: ['$helpers'],
    props: {
        fields: {
            type: Array,
            default: () => []
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
    methods: {
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        addFieldToForm () {
            this.$emit('handleModalEvent', true);
        },
        up (field) {
            this.$emit('upEvent', field);
        },
        down (field) {
            this.$emit('downEvent', field);
        },
        remove (formField) {
            this.$emit('removeFormFieldEvent', formField);
        },
        getType (type) {
            if (type === 1) {
                return this.$t('forms.form.field.type.text');
            } else if (type === 2) {
                return this.$t('forms.form.field.type.date');
            } else if (type === 3) {
                return this.$t('forms.form.field.type.list');
            } else {
                return this.$t('forms.form.field.type.text_box');
            }
        }
    },
    watch: {
        fields: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
