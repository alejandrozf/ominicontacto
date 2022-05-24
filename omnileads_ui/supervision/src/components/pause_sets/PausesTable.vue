<template>
  <div class="card">
    <DataTable
      :value="pausas"
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
      :filters="filters"
      filterDisplay="menu"
      :globalFilterFields="['pausa', 'representative.name']"
    >
      <template #header>
        <div class="p-d-flex p-jc-between">
          <Button
            type="button"
            icon="pi pi-filter-slash"
            :label="$t('globals.clean_filter')"
            class="p-button-outlined"
            @click="clearFilter()"
          />
          <div>
            <Button
              :label="$tc('globals.new')"
              icon="pi pi-plus"
              class="p-mr-2"
              @click="newPauseConfigModal"
              v-tooltip.top="'Nueva configuracion de pausa'"
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
        field="pause_name"
        :sortable="true"
        :header="$t('models.pause_setting.pause')"
      ></Column>
      <Column
        field="pause_type"
        :sortable="true"
        :header="$t('models.pause_setting.pause_type')"
      ></Column>
      <Column
        field="time_to_end_pause"
        :sortable="true"
        :header="$t('models.pause_setting.time_to_end_pause')"
      >
        <template #body="slotProps">
          {{
            slotProps.data.time_to_end_pause > 0
              ? formatTime(slotProps.data.time_to_end_pause)
              : $t("views.pause_sets.infinite_pause")
          }}
        </template>
      </Column>
      <Column :header="$tc('globals.option', 2)" :exportable="false">
        <template #body="slotProps">
          <Button
            icon="pi pi-pencil"
            class="p-button-warning p-ml-2"
            @click="editPauseConfig(slotProps.data)"
            v-tooltip.top="$t('globals.edit')"
          />

          <Button
            v-if="pausas.length >= 2"
            icon="pi pi-trash"
            class="p-button-danger p-ml-2"
            @click="removePauseConfig(slotProps.data.id)"
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
        pausas: {
            type: Array,
            default: () => []
        }
    },
    data () {
        return {
            filters: null,
            showModal: false
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
        newPauseConfigModal () {
            this.$emit('handleModal', true);
        },
        async removePauseConfig (id) {
            this.$swal({
                title: this.$t('globals.sure_notification'),
                icon: this.$t('globals.icon_warning'),
                showCancelButton: true,
                confirmButtonText: this.$t('globals.yes'),
                cancelButtonText: this.$t('globals.no'),
                confirmButtonColor: '#4CAF50',
                cancelButtonColor: '#D32F2F',
                backdrop: false,
                reverseButtons: true
            }).then(async (result) => {
                if (result.isConfirmed) {
                    this.$swal.fire({
                        title: this.$t('globals.processing_request'),
                        timerProgressBar: true,
                        allowOutsideClick: false,
                        didOpen: () => {
                            this.$swal.showLoading();
                        }
                    });
                    const resp = await this.deletePauseConfig(id);
                    this.$swal.close();
                    if (resp) {
                        this.$emit('initDataEvent');
                        this.$swal(
                            this.$helpers.getToasConfig(
                                this.$t('globals.success_notification'),
                                this.$tc('globals.success_deleted_type', {
                                    type: this.$tc('globals.pause_config')
                                }),
                                this.$t('globals.icon_success')
                            )
                        );
                    } else {
                        this.$swal(
                            this.$helpers.getToasConfig(
                                this.$t('globals.error_notification'),
                                this.$tc('globals.error_to_deleted_type', {
                                    type: this.$tc('globals.pause_config')
                                }),
                                this.$t('globals.icon_error')
                            )
                        );
                    }
                } else if (result.dismiss === this.$swal.DismissReason.cancel) {
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.cancelled'),
                            this.$t('views.pause_sets.pause_config_not_deleted'),
                            this.$t('globals.icon_error')
                        )
                    );
                }
            });
        },
        editPauseConfig (pauseConfig) {
            this.$emit('editPauseConfigEvent', pauseConfig);
        },
        formatTime (sec) {
            return this.$helpers.formatTime(sec);
        },
        ...mapActions(['deletePauseConfig'])
    },
    watch: {
        pausas: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
