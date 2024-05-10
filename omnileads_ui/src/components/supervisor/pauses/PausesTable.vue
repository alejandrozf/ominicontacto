<template>
  <div class="card">
    <DataTable
      :value="pausesFilter"
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
              @click="clearFilter()"
            />
          </div>
          <div class="flex align-items-center justify-content-center">
            <Button
              v-if="!showAllInfo"
              type="button"
              class="mr-2"
              :label="$t('views.external_sites.show_hiddens')"
              @click="handleShowData(true)"
            />
            <Button
              v-else
              type="button"
              class="mr-2 p-button-secondary"
              :label="$t('views.external_sites.remove_hiddens')"
              @click="handleShowData(false)"
            />
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
        field="nombre"
        :sortable="true"
        :header="$t('models.pause.name')"
      ></Column>
      <Column
        field="tipo"
        :sortable="true"
        :header="$t('models.pause.type')"
      >
        <template #body="{ data }">
          {{ data.tipo == 'P' ?  $t('forms.pause.types.opt1') : $t('forms.pause.types.opt2') }}
        </template>
      </Column>
      <Column
        :header="$t('models.pause.status')"
        dataType="boolean"
        field="eliminada"
        :sortable="true"
        style="max-width: 8rem"
      >
        <template #body="{ data }">
          <i
            v-if="!data.eliminada"
            class="pi pi-check-circle"
            style="color: green"
          ></i>
          <i v-else class="pi pi-times-circle" style="color: red"></i>
        </template>
      </Column>
      <Column :header="$tc('globals.option', 2)" style="max-width: 25rem">
        <template #body="slotProps">
          <Button
            icon="pi pi-pencil"
            class="p-button-warning ml-2"
            @click="toEditPause(slotProps.data)"
            v-tooltip.top="$t('globals.edit')"
          />
          <Button
            v-if="slotProps.data.eliminada"
            icon="pi pi-refresh"
            class="p-button-info ml-2"
            @click="reactivate(slotProps.data.id)"
            v-tooltip.top="$t('globals.reactivate')"
          />
          <Button
            v-else
            icon="pi pi-trash"
            class="p-button-danger ml-2"
            @click="remove(slotProps.data.id)"
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
import { HTTP_STATUS } from '@/globals';

export default {
    inject: ['$helpers'],
    props: {
        pauses: {
            type: Array,
            default: () => []
        }
    },
    data () {
        return {
            filters: null,
            showAllInfo: true,
            pausesFilter: []
        };
    },
    created () {
        this.initFilters();
        this.initDataTable();
    },
    methods: {
        handleShowData (status) {
            this.showAllInfo = status;
            this.initDataTable();
        },
        clearFilter () {
            this.initFilters();
        },
        initDataTable () {
            if (this.showAllInfo) {
                this.pausesFilter = this.pauses;
            } else {
                this.pausesFilter = this.pauses.filter(
                    (es) => es.eliminada === false
                );
            }
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        toEditPause (pause) {
            this.$emit('handleModalEvent', {
                showModal: true, formToCreate: false, pause
            });
        },
        async remove (id) {
            const { status, message } = await this.deletePause(id);
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initPauses();
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        message,
                        this.$t('globals.icon_success')
                    )
                );
            } else {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        message,
                        this.$t('globals.icon_error')
                    )
                );
            }
        },
        async reactivate (id) {
            const { status, message } = await this.reactivatePause(id);
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initPauses();
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        message,
                        this.$t('globals.icon_success')
                    )
                );
            } else {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        message,
                        this.$t('globals.icon_error')
                    )
                );
            }
        },
        ...mapActions([
            'deletePause',
            'reactivatePause',
            'initPauses'
        ])
    },
    watch: {
        pauses: {
            handler () {
                this.initDataTable();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
