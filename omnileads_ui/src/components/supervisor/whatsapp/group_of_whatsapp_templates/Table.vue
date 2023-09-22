<template>
  <div class="card">
    <DataTable
      :value="templates"
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
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="nombre"
        :sortable="true"
        :header="$t('models.whatsapp.group_of_whatsapp_template.nombre')"
      ></Column>
      <Column
        field="templates"
        :header="$t('models.whatsapp.group_of_whatsapp_template.templates')"
        style="max-width: 20rem"
      >
        <template #body="slotProps">
          {{ slotProps.data.templates.length }}
        </template>
      </Column>
      <Column
        :header="$t('models.whatsapp.group_of_whatsapp_template.status')"
        dataType="boolean"
        field="is_active"
        :sortable="true"
        style="max-width: 8rem"
      >
        <template #body="{ data }">
          <i
            v-if="!data.is_active"
            class="pi pi-check-circle"
            style="color: green"
          ></i>
          <i v-else class="pi pi-times-circle" style="color: red"></i>
        </template>
      </Column>
      <Column :header="$tc('globals.option', 2)" style="max-width: 20rem">
        <template #body="slotProps">
          <Button
            icon="pi pi-pencil"
            class="p-button-warning"
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
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { FilterMatchMode } from 'primevue/api';
import { HTTP_STATUS, CONFIRM_BTN_COLOR, CANCEL_BTN_COLOR } from '@/globals';

export default {
    inject: ['$helpers'],
    data () {
        return {
            filters: null,
            templates: []
        };
    },
    created () {
        this.initFilters();
    },
    computed: {
        ...mapState(['supWhatsappGroupOfWhatsappTemplates'])
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
        edit (id) {
            this.$router.push({
                name: 'supervisor_whatsapp_group_of_whatsapp_templates_edit',
                params: { id }
            });
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
                    const { status, message } =
            await this.deleteWhatsappGroupOfWhatsappTemplate(id);
                    this.$swal.close();
                    if (status === HTTP_STATUS.SUCCESS) {
                        this.initWhatsappGroupOfWhatsappTemplates();
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
                                type: this.$tc('globals.whatsapp.provider')
                            }),
                            this.$t('globals.icon_error')
                        )
                    );
                }
            });
        },
        ...mapActions([
            'deleteWhatsappGroupOfWhatsappTemplate',
            'initWhatsappGroupOfWhatsappTemplates'
        ])
    },
    watch: {
        supWhatsappGroupOfWhatsappTemplates: {
            handler () {
                this.templates = this.supWhatsappGroupOfWhatsappTemplates.map(
                    (t) => {
                        return {
                            id: t.id,
                            nombre: t.name,
                            templates: t.templates,
                            is_active: t.is_active
                        };
                    }
                );
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
