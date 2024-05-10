<template>
  <div class="card">
    <Toast />
    <DataTable
      :value="orderedOutboundRoutes"
      class="p-datatable-sm"
      showGridlines
      :scrollable="true"
      scrollHeight="600px"
      responsiveLayout="scroll"
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
      @rowReorder="onRowReorder"
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
              icon="pi pi-sort-alt"
              :label="$t('globals.reorder')"
              class="p-button-secondary ml-2"
              @click="orderRoutes"
            />
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column :rowReorder="true" headerStyle="width: 20px" ></Column>
      <Column
        field="id"
        :header="$t('models.outbound_route.id')"
      ></Column>
      <Column
        field="nombre"
        :header="$t('models.outbound_route.name')"
      ></Column>
      <Column
        field="ring_time"
        :header="$t('models.outbound_route.ring_time')"
      ></Column>
      <Column
        field="dial_options"
        :header="$t('models.outbound_route.dial_options')"
      ></Column>
      <Column
        :header="$tc('globals.option', 2)"
        style="max-width: 25rem"
        :exportable="false"
      >
        <template #body="slotProps">
          <Button
            icon="pi pi-eye"
            class="p-button-info ml-2"
            @click="detail(slotProps.data)"
            v-tooltip.top="$t('globals.show')"
          />
          <Button
            icon="pi pi-pencil"
            class="p-button-warning ml-2"
            @click="edit(slotProps.data.id)"
            v-tooltip.top="$t('globals.edit')"
          />
          <Button
            icon="pi pi-trash"
            class="p-button-danger ml-2"
            @click="remove(slotProps.data.id)"
            v-tooltip.top="$t('globals.delete')"
          />
        </template>
      </Column>
    </DataTable>
    <ModalOutboundRouteDetail :outboundRoute='outboundRouteDetail' :showModal='showModalDetail' @handleModalDetailEvent='handleModalDetail' />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { FilterMatchMode } from 'primevue/api';
import ModalOutboundRouteDetail from '@/components/supervisor/outbound_routes/ModalOutboundRouteDetail';
import { CONFIRM_BTN_COLOR, CANCEL_BTN_COLOR, HTTP_STATUS } from '@/globals';

export default {
    inject: ['$helpers'],
    props: {
        outboundRoutes: {
            type: Array,
            default: () => []
        }
    },
    components: {
        ModalOutboundRouteDetail
    },
    data () {
        return {
            filters: null,
            showModalDetail: false,
            orderedOutboundRoutes: [],
            outboundRouteDetail: {}
        };
    },
    created () {
        this.initFilters();
    },
    computed: {
        ...mapState(['orphanTrunks'])
    },
    methods: {
        ...mapActions(['initOutboundRoutes', 'deleteOutboundRoute', 'initOutboundRouteOrphanTrunks', 'reorderOutboundRoutes']),
        async orderRoutes () {
            const response = await this.reorderOutboundRoutes({ orden: this.orderedOutboundRoutes.map(r => r.id) });
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                this.initOutboundRoutes();
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
        onRowReorder (event) {
            this.orderedOutboundRoutes = event.value;
            this.$toast.add({ severity: 'success', summary: this.$t('forms.outbound_route.on_row_reorder'), life: 4000 });
        },
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        edit (id) {
            this.$router.push({
                name: 'supervisor_outbound_routes_edit',
                params: { id }
            });
        },
        detail (outboundRoute) {
            this.showModalDetail = true;
            this.outboundRouteDetail = outboundRoute;
        },
        handleModalDetail (showModal) {
            this.showModalDetail = showModal;
        },
        async getOrphanTrunksMessage (id) {
            await this.initOutboundRouteOrphanTrunks(id);
            if (this.orphanTrunks.length > 0) {
                var message = `<p>${this.$t('forms.outbound_route.validations.orphan_trunks')}</p>`;
                message += '<ul>';
                for (let i = 0; i < this.orphanTrunks.length; i++) {
                    const trunk = this.orphanTrunks[i];
                    message += `<li>${trunk.nombre}</li>`;
                }
                message += '</ul>';
                return message;
            } else {
                return null;
            }
        },
        async remove (id) {
            this.$swal({
                title: this.$t('globals.sure_notification'),
                icon: this.$t('globals.icon_warning'),
                showCancelButton: true,
                html: await this.getOrphanTrunksMessage(id),
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
                    const response = await this.deleteOutboundRoute(id);
                    this.$swal.close();
                    const { status, message } = response;
                    if (status === HTTP_STATUS.SUCCESS) {
                        await this.initOutboundRoutes();
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
                                type: this.$tc('globals.outbound_route')
                            }),
                            this.$t('globals.icon_error')
                        )
                    );
                }
            });
        }
    },
    watch: {
        outboundRoutes: {
            handler () {
                this.orderedOutboundRoutes = this.outboundRoutes;
            },
            deep: true,
            immediate: true
        },
        orphanTrunks: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
