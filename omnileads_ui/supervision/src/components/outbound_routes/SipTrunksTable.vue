<template>
  <div class="card">
    <DataTable
      :value="trunks"
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
      :globalFilterFields="['nombre']"
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
                  $t('globals.find_by', { field: $tc('globals.name', 1) })
                "
              />
            </span>
            <Button
              v-if="showOptions"
              type="button"
              icon="pi pi-plus"
              class="p-button-info ml-2"
              @click="newTrunk"
            />
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="nombre"
        :sortable="true"
        :header="$t('models.dial_pattern.prepend')"
      ></Column>
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
            @click="editTrunk(slotProps.data)"
            v-tooltip.top="$t('globals.edit')"
          />
          <Button
            v-if="trunks.length > 1"
            @click="remove(slotProps.data.id)"
            icon="pi pi-trash"
            class="p-button-danger ml-2"
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
        trunks: {
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
        newTrunk () {
            this.$emit('handleTrunkModalEvent', true, true, null);
        },
        editTrunk (trunk) {
            this.$emit('handleTrunkModalEvent', true, false, trunk);
        },
        remove (id) {
            this.removeTrunk(id);
            this.$emit('initTrunksEvent');
        },
        ...mapActions(['removeTrunk'])
    },
    watch: {
        trunks: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
