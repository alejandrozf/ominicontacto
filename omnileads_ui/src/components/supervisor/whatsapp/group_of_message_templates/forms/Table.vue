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
              v-if="!withoutTemplates"
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
        field="name"
        :header="$t('models.whatsapp.message_template.nombre')"
        :sortable="true"
      ></Column>
      <Column
        field="tipo"
        :header="$t('models.whatsapp.message_template.tipo')"
        :sortable="true"
      >
        <template #body="slotProps">
          {{ getType(slotProps.data.type) }}
        </template>
      </Column>
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
import { TEMPLATE_TYPES } from '@/globals/supervisor/whatsapp/message_template';

export default {
    inject: ['$helpers'],
    data () {
        return {
            filters: null,
            templateTypes: [
                {
                    name: this.$t('forms.whatsapp.message_template.types.text'),
                    value: TEMPLATE_TYPES.TEXT
                },
                {
                    name: this.$t('forms.whatsapp.message_template.types.image'),
                    value: TEMPLATE_TYPES.IMAGE
                },
                {
                    name: this.$t('forms.whatsapp.message_template.types.file'),
                    value: TEMPLATE_TYPES.FILE
                },
                {
                    name: this.$t('forms.whatsapp.message_template.types.audio'),
                    value: TEMPLATE_TYPES.AUDIO
                },
                {
                    name: this.$t('forms.whatsapp.message_template.types.video'),
                    value: TEMPLATE_TYPES.VIDEO
                },
                {
                    name: this.$t('forms.whatsapp.message_template.types.sticker'),
                    value: TEMPLATE_TYPES.STICKER
                },
                {
                    name: this.$t('forms.whatsapp.message_template.types.location'),
                    value: TEMPLATE_TYPES.LOCATION
                },
                {
                    name: this.$t('forms.whatsapp.message_template.types.contact'),
                    value: TEMPLATE_TYPES.CONTACT
                }
            ],
            templates: [],
            withoutTemplates: false
        };
    },
    created () {
        this.initFilters();
    },
    computed: {
        ...mapState(['supWhatsappMessageTemplates', 'supMessageTemplatesOfGroup'])
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
        getType (type) {
            return this.templateTypes.find((t) => t.value === type).name;
        },
        add () {
            this.$emit('handleModalEvent', {
                showModal: true
            });
        },
        remove (id) {
            this.removeMessageTemplateOfGroup(id);
            this.$swal(
                this.$helpers.getToasConfig(
                    this.$t('globals.success_notification'),
                    this.$tc('globals.success_deleted_type', {
                        type: this.$tc('globals.whatsapp.message_template')
                    }),
                    this.$t('globals.icon_success'),
                    this.$t('globals.how_to_save_changes')
                )
            );
        },
        setTemplates () {
            if (
                this.supMessageTemplatesOfGroup &&
        this.supMessageTemplatesOfGroup.length > 0
            ) {
                this.templates = this.supWhatsappMessageTemplates.filter((t) =>
                    this.supMessageTemplatesOfGroup.includes(t.id)
                );
            } else {
                this.templates = [];
            }
            if (
                JSON.stringify(
                    this.supWhatsappMessageTemplates
                        .map((t) => t.id)
                        .sort((a, b) => a - b)
                ) ===
        JSON.stringify(
            Array.from(this.supMessageTemplatesOfGroup).sort((a, b) => a - b)
        )
            ) {
                this.withoutTemplates = true;
            } else {
                this.withoutTemplates = false;
            }
        },
        ...mapActions(['removeMessageTemplateOfGroup'])
    },
    watch: {
        supMessageTemplatesOfGroup: {
            handler () {
                this.setTemplates();
            },
            deep: true,
            immediate: true
        },
        supWhatsappMessageTemplates: {
            handler () {
                this.setTemplates();
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
