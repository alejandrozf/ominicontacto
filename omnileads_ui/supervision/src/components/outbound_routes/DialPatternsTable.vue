<template>
  <div class="card">
    <DataTable
      :value="dialPatterns"
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
              @click="newDialPattern"
            />
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="prepend"
        :sortable="true"
        :header="$t('models.dial_pattern.prepend')"
      ></Column>
      <Column
        field="prefix"
        :sortable="true"
        :header="$t('models.dial_pattern.prefix')"
      ></Column>
      <Column
        field="match_pattern"
        :sortable="true"
        :header="$t('models.dial_pattern.pattern')"
      ></Column>
      <Column
        v-if="showOptions && dialPatterns.length > 1"
        :header="$tc('globals.option', 2)"
        style="max-width: 25rem"
        :exportable="false"
      >
        <template #body="slotProps">
          <Button
            icon="pi pi-pencil"
            class="p-button-warning ml-2"
            @click="editDialPattern(slotProps.data)"
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
import { mapActions } from 'vuex';
import { FilterMatchMode } from 'primevue/api';

export default {
    inject: ['$helpers'],
    props: {
        dialPatterns: {
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
    methods: {
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        newDialPattern () {
            this.$emit('handleDialPatternModalEvent', true, true, null);
        },
        editDialPattern (dialPattern) {
            this.$emit('handleDialPatternModalEvent', true, false, dialPattern);
        },
        remove (dialPattern) {
            this.removeDialPattern(dialPattern);
        },
        ...mapActions(['removeDialPattern'])
    },
    watch: {
        dialPatterns: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
