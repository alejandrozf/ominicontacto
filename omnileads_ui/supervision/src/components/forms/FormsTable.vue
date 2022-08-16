<template>
  <div class="card">
    <DataTable
      :value="formsFilter"
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
        :header="$t('models.form.name')"
      ></Column>
      <Column
        field="descripcion"
        :header="$t('models.form.description')"
      ></Column>
      <Column
        :header="$t('models.form.status')"
        dataType="boolean"
        field="oculto"
        :sortable="true"
        style="max-width: 8rem"
      >
        <template #body="{ data }">
          <i
            v-if="!data.oculto"
            class="pi pi-check-circle"
            style="color: green"
          ></i>
          <i v-else class="pi pi-times-circle" style="color: red"></i>
        </template>
      </Column>
      <Column
        :header="$tc('globals.option', 2)"
        style="max-width: 25rem"
        :exportable="false"
      >
        <template #body="slotProps">
          <Button
            v-if="slotProps.data.se_puede_modificar"
            icon="pi pi-pencil"
            class="p-button-warning ml-2"
            @click="edit(slotProps.data.id)"
            v-tooltip.top="$t('globals.edit')"
          />
          <Button
            icon="pi pi-info-circle"
            class="p-button-info ml-2"
            @click="detail(slotProps.data.id)"
            v-tooltip.top="$t('globals.show')"
          />
          <Button
            v-if="slotProps.data.se_puede_modificar"
            icon="pi pi-trash"
            class="p-button-danger ml-2"
            @click="remove(slotProps.data.id)"
            v-tooltip.top="$t('globals.delete')"
          />
          <Button
            icon="pi pi-eye"
            v-if="slotProps.data.oculto == true"
            class="ml-2"
            @click="show(slotProps.data.id)"
            v-tooltip.top="$t('views.external_sites.show')"
          />
          <Button
            icon="pi pi-eye-slash"
            v-if="slotProps.data.oculto == false"
            class="p-button-secondary ml-2"
            @click="hide(slotProps.data.id)"
            v-tooltip.top="$t('views.external_sites.hide')"
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
        forms: {
            type: Array,
            default: () => []
        }
    },
    data () {
        return {
            filters: null,
            showAllInfo: false,
            formsFilter: []
        };
    },
    created () {
        this.initFilters();
        this.initDataTable();
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
        handleShowData (status) {
            this.showAllInfo = status;
            this.initDataTable();
        },
        initDataTable () {
            if (this.showAllInfo) {
                this.formsFilter = this.forms;
            } else {
                this.formsFilter = this.forms.filter((es) => es.oculto === false);
            }
        },
        detail (id) {
            this.$router.push({
                name: 'forms_detail',
                params: { id: id }
            });
        },
        edit (id) {
            this.$router.push({
                name: 'forms_edit_step1',
                params: { id: id }
            });
        },
        async hide (id) {
            const resp = await this.hideForm(id);
            if (resp) {
                await this.initForms();
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        this.$tc('globals.success_hide_type', {
                            type: this.$tc('globals.form')
                        }),
                        this.$t('globals.icon_success')
                    )
                );
            } else {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        this.$tc('globals.error_to_hide_type', {
                            type: this.$tc('globals.form')
                        }),
                        this.$t('globals.icon_error')
                    )
                );
            }
        },
        async show (id) {
            const resp = await this.showForm(id);
            if (resp) {
                await this.initForms();
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.success_notification'),
                        this.$tc('globals.success_show_type', {
                            type: this.$tc('globals.form')
                        }),
                        this.$t('globals.icon_success')
                    )
                );
            } else {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        this.$tc('globals.error_to_show_type', {
                            type: this.$tc('globals.form')
                        }),
                        this.$t('globals.icon_error')
                    )
                );
            }
        },
        async remove (id) {
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
                    const resp = await this.deleteForm(id);
                    this.$swal.close();
                    if (resp) {
                        this.initForms();
                        this.$swal(
                            this.$helpers.getToasConfig(
                                this.$t('globals.success_notification'),
                                this.$tc('globals.success_deleted_type', {
                                    type: this.$tc('globals.form')
                                }),
                                this.$t('globals.icon_success')
                            )
                        );
                    } else {
                        this.$swal(
                            this.$helpers.getToasConfig(
                                this.$t('globals.error_notification'),
                                this.$tc('globals.error_to_deleted_type', {
                                    type: this.$tc('globals.form')
                                }),
                                this.$t('globals.icon_error')
                            )
                        );
                    }
                } else if (result.dismiss === this.$swal.DismissReason.cancel) {
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.cancelled'),
                            this.$tc('globals.error_to_deleted_type', {
                                type: this.$tc('globals.form')
                            }),
                            this.$t('globals.icon_error')
                        )
                    );
                }
            });
        },
        ...mapActions(['deleteForm', 'initForms', 'showForm', 'hideForm'])
    },
    watch: {
        forms: {
            handler () {
                this.initDataTable();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
