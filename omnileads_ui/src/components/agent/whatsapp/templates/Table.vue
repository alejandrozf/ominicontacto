<template>
  <div class="card">
    <DataTable
      :value="agtWhatsTemplates"
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
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="nombre"
        style="max-width: 15rem"
        :sortable="true"
        :header="$t('models.whatsapp.message_template.nombre')"
      ></Column>
      <Column
        field="configuracion"
        :header="$t('models.whatsapp.message_template.configuracion')"
      ></Column>
      <Column
        field="tipo"
        :header="$t('models.whatsapp.message_template.tipo')"
        :sortable="true"
        style="max-width: 15rem"
      >
        <template #body="slotProps">
          <Tag
            :icon="`pi ${getIconByType(slotProps.data.tipo)}`"
            :value="getType(slotProps.data.tipo)"
            :severity="getSeveretyByType(slotProps.data.tipo)"
            rounded
          ></Tag>
        </template>
      </Column>
      <Column :header="$tc('globals.option', 2)" style="max-width: 10rem">
        <template #body="slotProps">
          <Button
            icon="pi pi-send"
            class="p-button-secondary"
            @click="send(slotProps.data)"
            v-tooltip.top="$t('globals.send')"
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
import { notificationEvent } from '@/globals/agent/whatsapp';

export default {
    inject: ['$helpers'],
    data () {
        return {
            filters: null
        };
    },
    created () {
        this.initFilters();
        this.agtWhatsTemplatesInit();
    },
    computed: {
        ...mapState(['agtWhatsTemplates'])
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
        closeModal () {
            this.clearFilter();
            const event = new CustomEvent('onWhatsappTemplatesEvent', {
                detail: {
                    templates: false
                }
            });
            window.parent.document.dispatchEvent(event);
        },
        getType (type) {
            return type === 0 ? 'Plantilla mensaje' : 'Template Whatsapp';
        },
        getSeveretyByType (type) {
            return type === 0 ? 'info' : 'success';
        },
        getIconByType (type) {
            return type === 0 ? 'pi-copy' : 'pi-whatsapp';
        },
        async send (template) {
            try {
                const { status, message } = await this.agtWhatsTemplateSendMsg(template);
                this.closeModal();
                if (status === HTTP_STATUS.SUCCESS) {
                    await notificationEvent(
                        this.$t('globals.success_notification'),
                        message,
                        this.$t('globals.icon_success')
                    );
                } else {
                    await notificationEvent(
                        this.$t('globals.error_notification'),
                        message,
                        this.$t('globals.icon_error')
                    );
                }
            } catch (error) {
                console.error('Error al enviar template');
                console.error(error);
                await notificationEvent(
                    this.$t('globals.error_notification'),
                    'Error al enviar template',
                    this.$t('globals.icon_error')
                );
            }
        },
        ...mapActions(['agtWhatsTemplatesInit', 'agtWhatsTemplateSendMsg'])
    },
    watch: {
        agtWhatsTemplates: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
