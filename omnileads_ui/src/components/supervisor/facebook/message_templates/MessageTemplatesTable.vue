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
              class="ml-2"
              icon="pi pi-plus"
              v-tooltip.top="$t('globals.new')"
              @click="newMessageTemplate"
            />
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="nombre"
        :header="$t('models.whatsapp.message_template.nombre')"
        :sortable="true"
      ></Column>
      <Column
        field="tipo"
        :header="$t('models.whatsapp.message_template.tipo')"
        :sortable="true"
      >
        <template #body="slotProps">
          {{ getType(slotProps.data.tipo) }}
        </template>
      </Column>
      <Column :header="$tc('globals.option', 2)" style="max-width: 20rem">
        <template #body="slotProps">
          <Button
            icon="pi pi-pencil"
            class="p-button-warning ml-2"
            @click="edit(slotProps.data)"
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
import { TEMPLATE_TYPES } from '@/globals/supervisor/whatsapp/message_template';
import { HTTP_STATUS, CONFIRM_BTN_COLOR, CANCEL_BTN_COLOR } from '@/globals';

export default {
    inject: ['$helpers'],
    data () {
        return {
            filters: null,
            templates: [],
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
            ]
        };
    },
    created () {
        this.initFilters();
    },
    computed: {
        ...mapState(['supFacebookPageTemplates'])
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
        edit (messageTemplate) {
            this.$emit('handleModalEvent', {
                showModal: true,
                formToCreate: false,
                messageTemplate
            });
        },
        newMessageTemplate () {
            this.$emit('handleModalEvent', {
                showModal: true
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
                    const { status, message } = await this.deleteFacebookPageTemplate(
                        id
                    );
                    this.$swal.close();
                    if (status === HTTP_STATUS.SUCCESS) {
                        this.initFacebookPageTemplates();
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
                                type: this.$tc('globals.whatsapp.message_template')
                            }),
                            this.$t('globals.icon_error')
                        )
                    );
                }
            });
        },
        ...mapActions([
            'deleteFacebookPageTemplate',
            'initFacebookPageTemplates',
            'initFacebookPageTemplate'
        ])
    },
    watch: {
        supFacebookPageTemplates: {
            handler () {
                this.templates = this.supFacebookPageTemplates.map((template) => {
                    return {
                        id: template.id,
                        nombre: template.name,
                        tipo: template.type,
                        configuracion: template.configuration
                    };
                });
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
