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
            <Button
              class="p-button-secondary ml-2"
              icon="pi pi-plus"
              v-tooltip.top="$t('globals.new')"
              @click="add"
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
      <Column :header="$tc('globals.option', 2)" style="max-width: 20rem">
        <template #body="slotProps">
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
        ...mapState(['supWhatsappTemplates', 'supWhatsappTemplatesOfGroup'])
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
        add () {
            this.$emit('handleModalEvent', {
                showModal: true
            });
        },
        remove (id) {
            this.removeWhatsappTemplateOfGroup(id);
            this.$swal(
                this.$helpers.getToasConfig(
                    this.$t('globals.success_notification'),
                    this.$tc('globals.success_deleted_type', {
                        type: this.$tc('globals.whatsapp.whatsapp_template')
                    }),
                    this.$t('globals.icon_success'),
                    this.$t('globals.how_to_save_changes')
                )
            );
        },
        setTemplates () {
            if (
                this.supWhatsappTemplatesOfGroup &&
        this.supWhatsappTemplatesOfGroup.length > 0
            ) {
                this.templates = this.supWhatsappTemplates.filter((t) =>
                    this.supWhatsappTemplatesOfGroup.includes(t.id)
                );
            } else {
                this.templates = [];
            }
        },
        ...mapActions(['removeWhatsappTemplateOfGroup'])
    },
    watch: {
        supWhatsappTemplatesOfGroup: {
            handler () {
                this.setTemplates();
            },
            deep: true,
            immediate: true
        },
        supWhatsappTemplates: {
            handler () {
                this.setTemplates();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
