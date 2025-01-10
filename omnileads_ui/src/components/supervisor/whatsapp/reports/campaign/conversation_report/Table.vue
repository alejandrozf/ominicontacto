<template>
  <div class="card">
    <DataTable
      ref="dt"
      :value="supWhatsReportCampaignConversations"
      class="p-datatable-sm"
      showGridlines
      :scrollable="true"
      scrollHeight="900px"
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
    >
      <template #header>
        <div class="flex justify-content-between flex-wrap">
          <div class="flex align-items-center justify-content-center">
            <h2>
              {{
                $t("views.whatsapp.reports.campaign.conversation.table_title")
              }}
              ({{ supWhatsReportCampaignConversations.length }})
            </h2>
          </div>
          <div class="flex align-items-center justify-content-center">
            <Button
              type="button"
              icon="pi pi-filter-slash"
              :label="$t('globals.clean_filter')"
              class="p-button-outlined"
              @click="cleanFilters()"
            />
            <Button icon="pi pi-external-link" :label="$t('globals.export_type', { type: 'CSV' })" @click="exportCSV($event)" />
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="agent.name"
        :sortable="true"
        :header="$t('models.whatsapp.conversation.agent')"
      >
        <template #body="{ data }">
          <Tag
            :icon="getAgentIcon(data.agent)"
            :severity="getAgentColor(data.agent)"
            :value="getAgentValue(data.agent)"
            rounded
          ></Tag>
        </template>
      </Column>
      <Column
        field="timestamp"
        :sortable="true"
        :header="$t('models.whatsapp.conversation.timestamp')"
        >
        <template #body="{ data }">
          {{ getDatetimeFormat(data.timestamp) }}
        </template>
      </Column>
      <Column
        field="campaign.name"
        :sortable="true"
        :header="$t('models.whatsapp.conversation.campaign')"
      ></Column>
      <Column
        field="campaign.type"
        :sortable="true"
        :header="$t('models.whatsapp.conversation.campaign_type')"
      >
        <template #body="{ data }">
          {{ getCampaignType(data.campaign.type) }}
        </template>
      </Column>
      <Column
        field="destination"
        :sortable="true"
        :header="$t('models.whatsapp.conversation.destination')"
      >
        <template #body="{ data }">
          <Tag
            icon="pi pi-phone"
            severity="info"
            :value="data.destination"
            rounded
          ></Tag>
        </template>
      </Column>
      <Column
        field="line.name"
        :sortable="true"
        :header="$t('models.whatsapp.conversation.line')"
      ></Column>
      <Column
        field="expire"
        :sortable="true"
        :header="$t('models.whatsapp.conversation.expire')"
      >
        <template #body="{ data }">
          <Tag
            :icon="getIcon(data.expire)"
            :severity="getColor(data.expire)"
            :value="getDatetimeFormat(data.expire)"
            rounded
          ></Tag>
        </template>
      </Column>
      <Column
        field="date_last_interaction"
        :sortable="true"
        :header="$t('models.whatsapp.conversation.last_interaction')"
      >
        <template #body="{ data }">
          <Tag
            icon="pi pi-calendar"
            style="background-color: #e5e5e5; color: #000000; font-weight: bold;"
            :value="getDatetimeFormat(data.date_last_interaction)"
            rounded
          ></Tag>
        </template>
      </Column>
      <Column
        field="is_active"
        :sortable="true"
        dataType="boolean"
        style="max-width: 8rem; text-align: center"
        :header="$t('models.whatsapp.conversation.is_active')"
      >
        <template #body="{ data }">
          <i
            v-if="data.is_active"
            class="pi pi-check-circle"
            style="color: green; font-size: 2rem"
          ></i>
          <i
            v-else
            class="pi pi-times-circle"
            style="color: red; font-size: 2rem"
          ></i>
        </template>
      </Column>
      <Column
        field="message_number"
        :sortable="true"
        style="max-width: 8rem; text-align: center"
        :header="$t('models.whatsapp.conversation.message')"
      >
        <template #body="slotProps">
          <i
            v-badge="slotProps.data.message_number"
            class="pi pi-comments p-overlay-badge"
            style="font-size: 2rem"
          />
        </template>
      </Column>
      <Column
        field="was_closed_by_system"
        :sortable="true"
        :header="$t('views.whatsapp.reports.campaign.conversation.system_closed')"
      >
      <template #body="{ data }">
        <i
          v-if="data.was_closed_by_system"
          class="pi pi-check-circle"
          style="color: green; font-size: 2rem"
        ></i>
        <i
          v-else
          class="pi pi-times-circle"
          style="color: red; font-size: 2rem"
        ></i>
      </template>
      </Column>
      <Column
        field="disposition.name"
        :sortable="true"
        :header="$t('models.whatsapp.conversation.disposition')"
      ></Column>
      <Column
        :header="$tc('globals.option', 2)"
        style="max-width: 8rem; text-align: center"
      >
        <template #body="slotProps">
          <Button
            icon="pi pi-eye"
            class="p-button-secondary"
            @click="showConversation(slotProps.data)"
            v-tooltip.top="$tc('globals.show', 1)"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { PROVIDER_TYPES } from '@/globals/supervisor/whatsapp/provider';
import { CAMPAIGN_TYPES } from '@/globals';

export default {
    inject: ['$helpers'],
    data () {
        return {
            campaignTypes: [
                { name: '-------', value: null },
                {
                    name: this.$t('models.campaign.types.manual'),
                    value: CAMPAIGN_TYPES.MANUAL
                },
                {
                    name: this.$t('models.campaign.types.dialer'),
                    value: CAMPAIGN_TYPES.DIALER
                },
                {
                    name: this.$t('models.campaign.types.inbound'),
                    value: CAMPAIGN_TYPES.ENTRANTE
                },
                {
                    name: this.$t('models.campaign.types.preview'),
                    value: CAMPAIGN_TYPES.PREVIEW
                }
            ]
        };
    },
    created () {},
    computed: {
        ...mapState(['supWhatsReportCampaignConversations'])
    },
    methods: {
        cleanFilters () {
            this.$emit('cleanFiltersEvent');
        },
        async showConversation (conversation) {
            await this.agtWhatsConversationDetail({ conversationId: conversation.id, $t: this.$t });
            this.$emit('handleModalEvent', {
                showModal: true,
                id: conversation.id
            });
        },
        getCampaignType (type) {
            return this.campaignTypes.find((c) => c.value === type).name;
        },
        getIcon (expired) {
            const currentDate = new Date();
            const expiredDate = new Date(expired);
            if (expiredDate.getTime() < currentDate.getTime()) {
                return 'pi pi-exclamation-triangle';
            } else if (expiredDate.getTime() > currentDate.getTime()) {
                return 'pi pi-check-circle';
            }
        },
        getAgentIcon (agent) {
            if (agent) {
                return 'pi pi-user';
            } else {
                return 'pi pi-user-minus';
            }
        },
        getAgentColor (agent) {
            if (agent) {
                return 'info';
            } else {
                return 'warning';
            }
        },
        getAgentValue (agent) {
            if (agent) {
                return agent.name;
            } else {
                return this.$t(
                    'forms.whatsapp.reports.campaign.conversation.form_filters.placeholders.without_agent'
                );
            }
        },
        getColor (expired) {
            const currentDate = new Date();
            const expiredDate = new Date(expired);
            if (expiredDate.getTime() < currentDate.getTime()) {
                return 'warning';
            } else if (expiredDate.getTime() > currentDate.getTime()) {
                return 'success';
            }
        },
        getDatetimeFormat (date) {
            return this.$helpers.getDatetimeFormat(date);
        },
        getProvider (option) {
            if (option === PROVIDER_TYPES.TWILIO) {
                return this.$t('forms.whatsapp.provider.types.twilio');
            }
        },
        exportCSV() {
            this.$refs.dt.exportCSV();
        },
        ...mapActions(['initWhatsappProviders', 'agtWhatsConversationDetail'])
    },
    watch: {
        supWhatsReportCampaignConversations: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
