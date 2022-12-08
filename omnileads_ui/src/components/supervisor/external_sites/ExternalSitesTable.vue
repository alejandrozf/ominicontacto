<template>
  <div class="card">
    <DataTable
      :value="externalSitesFilter"
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
        :header="$t('models.external_site.name')"
      ></Column>
      <Column
        field="metodo"
        :sortable="true"
        :header="$t('models.external_site.method')"
      >
        <template #body="slotProps">
          {{ getMethod(slotProps.data.metodo) }}
        </template>
      </Column>
      <Column
        field="disparador"
        :sortable="true"
        :header="$t('models.external_site.trigger')"
      >
        <template #body="slotProps">
          {{ getTigger(slotProps.data.disparador) }}
        </template>
      </Column>
      <Column
        :header="$t('models.external_site.status')"
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
      <Column :header="$tc('globals.option', 2)" :exportable="false">
        <template #body="slotProps">
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
          <Button
            icon="pi pi-pencil"
            class="p-button-warning ml-2"
            @click="toEditExternalSite(slotProps.data)"
            v-tooltip.top="$t('globals.edit')"
          />
          <Button
            icon="pi pi-trash"
            class="p-button-danger ml-2"
            @click="remove(slotProps.data.id)"
            v-tooltip.top="$t('globals.delete')"
          />
          <Button
            icon="pi pi-info-circle"
            class="p-button-info ml-2"
            @click="showExternalSiteDetail(slotProps.data)"
            v-tooltip.top="$t('globals.show')"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import { FilterMatchMode } from 'primevue/api';
import { CONFIRM_BTN_COLOR, CANCEL_BTN_COLOR, HTTP_STATUS } from '@/globals';

export default {
    inject: ['$helpers'],
    props: {
        externalSites: {
            type: Array,
            default: () => []
        }
    },
    data () {
        return {
            filters: null,
            showAllInfo: false,
            externalSitesFilter: []
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
                this.externalSitesFilter = this.externalSites;
            } else {
                this.externalSitesFilter = this.externalSites.filter(
                    (es) => es.oculto === false
                );
            }
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        showExternalSiteDetail (externalSite) {
            this.$emit('showDetail', externalSite);
        },
        getMethod (option) {
            if (option === 1) {
                return this.$t('forms.external_site.methods.get');
            } else {
                return this.$t('forms.external_site.methods.post');
            }
        },
        getTigger (option) {
            if (option === 1) {
                return this.$t('forms.external_site.triggers.opt1');
            } else if (option === 2) {
                return this.$t('forms.external_site.triggers.opt2');
            } else if (option === 3) {
                return this.$t('forms.external_site.triggers.opt3');
            } else if (option === 4) {
                return this.$t('forms.external_site.triggers.opt4');
            }
        },
        toEditExternalSite (externalSite) {
            this.$router.push({
                name: 'supervisor_external_sites_update',
                params: { id: externalSite.id },
                props: { externalSite }
            });
        },
        async hide (id) {
            const { status, message } = await this.hideExternalSite(id);
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initExternalSites();
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
        async show (id) {
            const { status, message } = await this.showExternalSite(id);
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initExternalSites();
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
        async remove (id) {
            this.$swal({
                title: this.$t('globals.sure_notification'),
                icon: this.$t('globals.icon_warning'),
                showCancelButton: true,
                confirmButtonText: this.$t('globals.yes'),
                cancelButtonText: this.$t('globals.no'),
                confirmButtonColor: CONFIRM_BTN_COLOR,
                cancelButtonColor: CANCEL_BTN_COLOR,
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
                    const { status, message } = await this.deleteExternalSite(id);
                    this.$swal.close();
                    if (status === HTTP_STATUS.SUCCESS) {
                        this.initExternalSites();
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
                } else if (result.dismiss === this.$swal.DismissReason.cancel) {
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.cancelled'),
                            this.$tc('globals.error_to_deleted_type', {
                                type: this.$tc('globals.external_site')
                            }),
                            this.$t('globals.icon_error')
                        )
                    );
                }
            });
        },
        ...mapActions([
            'deleteExternalSite',
            'hideExternalSite',
            'showExternalSite',
            'initExternalSites'
        ])
    },
    watch: {
        externalSites: {
            handler () {
                this.initDataTable();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
