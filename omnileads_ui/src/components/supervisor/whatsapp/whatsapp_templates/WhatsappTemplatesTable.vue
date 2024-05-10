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
              class="ml-2 bg-teal-500"
              icon="pi pi-sync"
              v-tooltip.top="$t('globals.sync')"
              @click="syncUp"
            />
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="nombre"
        :header="$t('models.whatsapp.whatsapp_template.nombre')"
      ></Column>
      <Column
        field="idioma"
        :header="$t('models.whatsapp.whatsapp_template.idioma')"
        :sortable="true"
      ></Column>
      <Column
        field="status"
        :header="$t('models.whatsapp.whatsapp_template.status')"
        :sortable="true"
      ></Column>
      <Column
        field="tipo"
        :header="$t('models.whatsapp.whatsapp_template.tipo')"
      ></Column>
      <Column
        :header="$t('models.whatsapp.whatsapp_template.active')"
        dataType="boolean"
        field="is_active"
        :sortable="true"
        style="max-width: 8rem; text-align: center"
      >
        <template #body="{ data }">
          <i
            v-if="data.is_active"
            class="pi pi-check-circle"
            style="color: green"
          ></i>
          <i v-else class="pi pi-times-circle" style="color: red"></i>
        </template>
      </Column>
      <Column :header="$tc('globals.option', 2)" style="max-width: 10rem">
        <template #body="slotProps">
          <Button
            v-if="slotProps.data.is_active"
            icon="pi pi-eye-slash"
            class="p-button-secondary ml-2"
            @click="changeStatus(slotProps.data)"
            v-tooltip.top="$t('globals.deactivate')"
          />
          <Button
            v-else
            icon="pi pi-eye"
            class="p-button-primary ml-2"
            @click="changeStatus(slotProps.data)"
            v-tooltip.top="$t('globals.activate')"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { FilterMatchMode } from 'primevue/api';
import { HTTP_STATUS } from '@/globals';

export default {
    inject: ['$helpers'],
    data () {
        return {
            filters: null,
            id: null,
            templates: []
        };
    },
    created () {
        this.initFilters();
        this.id = this.$route.params.id;
    },
    computed: {
        ...mapState(['supWhatsappTemplates'])
    },
    methods: {
        ...mapActions([
            'sycnupWhatsappTemplates',
            'initSupWhatsappTemplates',
            'whatsappTemplateStatusChange'
        ]),
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        async syncUp () {
            this.$helpers.openLoader(this.$t);
            const { status, message } = await this.sycnupWhatsappTemplates(this.id);
            this.$helpers.closeLoader();
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initSupWhatsappTemplates();
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
        async changeStatus (template) {
            this.$helpers.openLoader(this.$t);
            const { status, message } = await this.whatsappTemplateStatusChange({
                templateId: template.id,
                lineId: this.id
            });
            this.$helpers.closeLoader();
            if (status === HTTP_STATUS.SUCCESS) {
                await this.initSupWhatsappTemplates();
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
        }
    },
    watch: {
        supWhatsappTemplates: {
            handler () {
                if (this.supWhatsappTemplates.length > 0) {
                    this.templates = this.supWhatsappTemplates
                        .filter((wt) => parseInt(wt.line) === parseInt(this.id))
                        .map((wt) => {
                            return {
                                id: wt.id,
                                linea: wt.line,
                                nombre: wt.name,
                                idioma: wt.language,
                                status: wt.status,
                                tipo: wt.type,
                                identificador: wt.identifier,
                                created: wt.created,
                                updated: wt.updated,
                                is_active: wt.is_active
                            };
                        });
                } else {
                    this.templates = [];
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
