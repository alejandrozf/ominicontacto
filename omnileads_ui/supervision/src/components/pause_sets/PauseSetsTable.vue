<template>
  <div class="card">
    <DataTable
      :value="pauseSets"
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
      :globalFilterFields="['nombre', 'representative.name']"
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
      <Column field="id" :header="$t('models.pause_set.id')"></Column>
      <Column
        field="nombre"
        :sortable="true"
        :header="$t('models.pause_set.name')"
      ></Column>
      <Column :header="$tc('globals.option', 2)" style="max-width: 25rem">
        <template #body="slotProps">
          <Button
            icon="pi pi-eye"
            class="p-button-info ml-2"
            @click="toPauseSetDetail(slotProps.data.id)"
            v-tooltip.top="$t('globals.show')"
          />
          <Button
            icon="pi pi-pencil"
            class="p-button-warning ml-2"
            @click="editGroup(slotProps.data)"
            v-tooltip.top="$t('globals.edit')"
          />
          <Button
            icon="pi pi-trash"
            class="p-button-danger ml-2"
            @click="removePauseGroup(slotProps.data.id)"
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
        pauseSets: {
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
        toPauseSetDetail (id) {
            this.$router.push({ name: 'pause_sets_detail', params: { id: id } });
        },
        editGroup (group) {
            this.$emit('editGroupEvent', group);
        },
        async removePauseGroup (id) {
            this.$swal({
                title: this.$t('globals.sure_notification'),
                text: this.$t('views.pause_sets.pause_settings_will_be_deleted'),
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
                    const resp = await this.deletePauseSet(id);
                    this.$swal.close();
                    if (resp) {
                        this.initPauseSets();
                        this.$swal(
                            this.$helpers.getToasConfig(
                                this.$t('globals.success_notification'),
                                this.$tc('globals.success_deleted_type', {
                                    type: this.$tc('globals.pause_set')
                                }),
                                this.$t('globals.icon_success')
                            )
                        );
                    } else {
                        this.$swal(
                            this.$helpers.getToasConfig(
                                this.$t('globals.error_notification'),
                                this.$tc('globals.error_to_deleted_type', {
                                    type: this.$tc('globals.pause_set')
                                }),
                                this.$t('globals.icon_error')
                            )
                        );
                    }
                } else if (result.dismiss === this.$swal.DismissReason.cancel) {
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.cancelled'),
                            this.$t('views.pause_sets.pause_sets_not_deleted'),
                            this.$t('globals.icon_error')
                        )
                    );
                }
            });
        },
        ...mapActions(['deletePauseSet', 'initPauseSets'])
    }
};
</script>
