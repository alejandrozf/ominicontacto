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
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        async syncUp () {
            const { status, message } = await this.sycnupWhatsappTemplates(this.id);
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
        ...mapActions([
            'sycnupWhatsappTemplates',
            'initSupWhatsappTemplates'
        ])
    },
    watch: {
        supWhatsappTemplates: {
            handler () {
                if (this.supWhatsappTemplates.length > 0) {
                    this.templates = this.supWhatsappTemplates.filter(wt => parseInt(wt.line) === parseInt(this.id)).map(
                        (wt) => {
                            return {
                                id: wt.id,
                                linea: wt.line,
                                nombre: wt.name,
                                idioma: wt.language,
                                status: wt.status,
                                tipo: wt.type,
                                identificador: wt.identifier,
                                created: wt.created,
                                updated: wt.updated
                            };
                        }
                    );
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
