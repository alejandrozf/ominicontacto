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
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="name"
        style="max-width: 15rem"
        :sortable="true"
        :header="$t('models.whatsapp.message_template.nombre')"
      ></Column>
      <Column
        field="configuration.text"
        :header="$t('models.whatsapp.message_template.configuracion')"
      ></Column>
      <Column
        field="type"
        :header="$t('models.whatsapp.message_template.tipo')"
        :sortable="true"
        style="max-width: 15rem"
      >
        <template #body="slotProps">
          <Tag
            :icon="`pi ${getIconByType(slotProps.data.type)}`"
            :value="getType(slotProps.data.type)"
            :severity="getSeveretyByType(slotProps.data.type)"
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
import { TEMPLATE_TYPES } from '@/globals/supervisor/facebook';
import { notificationEvent, NOTIFICATION } from '@/globals/agent/facebook';

export default {
    inject: ['$helpers'],
    props: {
        onlyWhatsappTemplates: {
            type: Boolean,
            default: false
        }
    },
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
        ...mapState(['supCampaignFacebookTemplates', 'agtFacebookConversationInfo'])
    },
    methods: {
        ...mapActions(['agtFacebookConversationSendTemplateMessage']),
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
            const event = new CustomEvent('onFacebookTemplatesEvent', {
                detail: {
                    templates: false,
                    conversationId: null
                }
            });
            window.parent.document.dispatchEvent(event);
            window.location.reload();
        },
        setParamsToTemplate (template) {
            this.$emit('handleModalEvent', {
                showModal: true,
                template,
                conversationId: this.agtFacebookConversationInfo.id
            });
        },
        getType (type) {
            return type === TEMPLATE_TYPES.FACEBOOK
                ? this.$t('models.facebook.templates.message_template')
                : this.$t('models.facebook.templates.whatsapp_template');
        },
        getSeveretyByType (type) {
            return type === TEMPLATE_TYPES.FACEBOOK ? 'info' : 'success';
        },
        getIconByType (type) {
            return type === TEMPLATE_TYPES.FACEBOOK ? 'pi-copy' : 'pi-whatsapp';
        },
        async send (template) {
            try {
                const messages = JSON.parse(
                    localStorage.getItem('agtFacebookConversationMessages')
                );
                let result = null;
                if (template.type === TEMPLATE_TYPES.FACEBOOK) {
                    console.log('Sending Facebook template - messages', messages);
                    console.log('Sending Facebook template message', template);
                    this.$helpers.openLoader(this.$t);
                    result = await this.agtFacebookConversationSendTemplateMessage({
                        conversationId: this.agtFacebookConversationInfo.id,
                        templateId: template.id,
                        pageId: this.agtFacebookConversationInfo.page.page_id,
                        messages: messages,
                        $t: this.$t
                    });
                }
                this.$helpers.closeLoader();
                const { status, message } = result;
                console.log('Send template result:', result);
                this.closeModal();
                if (status === HTTP_STATUS.SUCCESS) {
                    await notificationEvent(
                        NOTIFICATION.TITLES.SUCCESS,
                        message,
                        NOTIFICATION.ICONS.SUCCESS
                    );
                } else {
                    await notificationEvent(
                        NOTIFICATION.TITLES.ERROR,
                        message,
                        NOTIFICATION.ICONS.ERROR
                    );
                }
            } catch (error) {
                console.error('Error al enviar template');
                console.error(error);
                await notificationEvent(
                    NOTIFICATION.TITLES.ERROR,
                    'Error al enviar template',
                    NOTIFICATION.ICONS.ERROR
                );
            }
        },
    },
    watch: {
        supCampaignFacebookTemplates: {
            handler () {
              this.templates = this.supCampaignFacebookTemplates;
            },
            deep: true,
            immediate: true
        },
        agtFacebookConversationInfo: {
            handler () {},
            deep: true,
            immediate: true
        },
        onlyWhatsappTemplates: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
