<template>
  <div class="card">
    <DataTable
      :value="externalSystems"
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
        <div class="p-d-flex p-jc-between">
          <Button
            type="button"
            icon="pi pi-filter-slash"
            :label="$t('globals.clean_filter')"
            class="p-button-outlined"
            @click="clearFilter()"
          />
          <div>
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
        :header="$t('models.external_system.name')"
      ></Column>
      <Column
        :header="$tc('globals.option', 2)"
        style="max-width: 25rem"
        :exportable="false"
      >
        <template #body="slotProps">
          <Button
            icon="pi pi-pencil"
            class="p-button-warning p-ml-2"
            @click="edit(slotProps.data.id)"
            v-tooltip.top="$t('globals.edit')"
          />
          <Button
            icon="pi pi-info-circle"
            class="p-button-info p-ml-2"
            @click="detail(slotProps.data.id)"
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

export default {
    inject: ['$helpers'],
    props: {
        externalSystems: {
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
        detail (id) {
            this.$router.push({
                name: 'external_systems_detail',
                params: { id: id }
            });
        },
        edit (id) {
            this.$router.push({
                name: 'external_systems_edit',
                params: { id: id }
            });
        },
        // async remove (id) {
        //     this.$swal({
        //         title: this.$t('globals.sure_notification'),
        //         icon: this.$t('globals.icon_warning'),
        //         showCancelButton: true,
        //         confirmButtonText: this.$t('globals.yes'),
        //         cancelButtonText: this.$t('globals.no'),
        //         backdrop: false,
        //         reverseButtons: true
        //     }).then(async (result) => {
        //         if (result.isConfirmed) {
        //             this.$swal.fire({
        //                 title: this.$t('globals.processing_request'),
        //                 timerProgressBar: true,
        //                 allowOutsideClick: false,
        //                 didOpen: () => {
        //                     this.$swal.showLoading();
        //                 }
        //             });
        //             const resp = await this.deleteExternalSite(id);
        //             this.$swal.close();
        //             if (resp) {
        //                 this.initExternalSites();
        //                 this.$swal(
        //                     this.$helpers.getToasConfig(
        //                         this.$t('globals.success_notification'),
        //                         this.$tc('globals.success_deleted_type', {
        //                             type: this.$tc('globals.external_site')
        //                         }),
        //                         this.$t('globals.icon_success')
        //                     )
        //                 );
        //             } else {
        //                 this.$swal(
        //                     this.$helpers.getToasConfig(
        //                         this.$t('globals.error_notification'),
        //                         this.$tc('globals.error_to_deleted_type', {
        //                             type: this.$tc('globals.external_site')
        //                         }),
        //                         this.$t('globals.icon_error')
        //                     )
        //                 );
        //             }
        //         } else if (result.dismiss === this.$swal.DismissReason.cancel) {
        //             this.$swal(
        //                 this.$helpers.getToasConfig(
        //                     this.$t('globals.cancelled'),
        //                     this.$tc('globals.error_to_deleted_type', {
        //                         type: this.$tc('globals.external_site')
        //                     }),
        //                     this.$t('globals.icon_error')
        //                 )
        //             );
        //         }
        //     });
        // },
        ...mapActions(['deleteExternalSystem', 'initExternalSystems'])
    },
    watch: {
        externalSystems: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
