<template>
  <div class="card">
    <DataTable
      :value="agtWhatsDispositionChatHistory"
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
      :globalFilterFields="['contact.phone']"
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
                  $t('globals.find_by', {
                    field: $t('models.whatsapp.disposition_form.phone'),
                  })
                "
              />
            </span>
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="agent"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.agent')"
      >
        <template #body="slotProps">
          {{ getAgent(slotProps.data.agent) }}
        </template>
      </Column>
      <Column
        field="contact.phone"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.contact_phone')"
      >
        <template #body="slotProps">
          {{ getContactPhone(slotProps.data.contact) }}
        </template>
      </Column>
      <Column
        field="contact.data"
        :header="$t('models.whatsapp.disposition_form.contact_data')"
      >
        <template #body="slotProps">
          {{ getContactData(slotProps.data.contact) }}
        </template>
      </Column>
      <Column
        field="disposition_data.type"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.disposition_option')"
      >
        <template #body="slotProps">
          {{ getDispositionOption(slotProps.data.disposition_data.type) }}
        </template>
      </Column>
      <Column
        field="disposition_data.name"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.disposition')"
      >
        <template #body="slotProps">
          {{ slotProps.data.disposition_data.name }}
        </template>
      </Column>
      <Column
        field="campaign.type"
        :header="$t('models.whatsapp.disposition_form.campaign_type')"
      >
        <template #body="slotProps">
          {{ getCampaignType(slotProps.data.campaign.type) }}
        </template>
      </Column>
      <Column
        field="campaign.name"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.campaign')"
      >
        <template #body="slotProps">
          {{ slotProps.data.campaign.name }}
        </template>
      </Column>
      <Column
        field="updated_at"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.created_at')"
      >
        <template #body="slotProps">
          {{ timeFormat(slotProps.data.updated_at) }}
        </template>
      </Column>
      <!-- <Column :header="$tc('globals.option', 2)" style="max-width: 10rem">
        <template #body="slotProps">
          <Button
            icon="pi pi-eye"
            class="p-button-secondary"
            @click="show(slotProps.data)"
            v-tooltip.top="$t('globals.show')"
          />
        </template>
      </Column> -->
    </DataTable>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { FilterMatchMode } from 'primevue/api';
import {
    FORM_TYPES
} from '@/globals/agent/whatsapp/disposition';
import {
    CAMPAIGN_TYPES
} from '@/globals';

export default {
    inject: ['$helpers'],
    data () {
        return {
            filters: null,
            types: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.disposition_chat.form_types.no_action'),
                    value: FORM_TYPES.OPT1
                },
                {
                    name: this.$t(
                        'forms.whatsapp.disposition_chat.form_types.management'
                    ),
                    value: FORM_TYPES.OPT2
                },
                {
                    name: this.$t('forms.whatsapp.disposition_chat.form_types.schedule'),
                    value: FORM_TYPES.OPT3
                }
            ],
            campaignTypes: [
                { name: '-------', value: null },
                {
                    name: this.$t('models.campaign.types.manual'),
                    value: CAMPAIGN_TYPES.MANUAL
                },
                {
                    name: this.$t(
                        'models.campaign.types.dialer'
                    ),
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
    created () {
        this.initFilters();
    },
    computed: {
        ...mapState(['agtWhatsDispositionChatHistory'])
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
        timeFormat (val) {
            return new Date(val).toLocaleString();
        },
        phoneFormat (phone) {
            return phone
                .replace(/\D+/g, '')
                .replace(/(\d{1})(\d{3})(\d{3})(\d{4})/, '+$1 ($2) $3-$4');
        },
        getAgent (agent) {
            return agent?.name || '-------';
        },
        getContactPhone (contact) {
            return this.phoneFormat(contact.phone);
        },
        getContactData (contact) {
            return contact.data;
        },
        getDispositionOption (option) {
            return this.types.find((item) => item.value === option)?.name || '-------';
        },
        getCampaignType (type) {
            return this.campaignTypes.find((item) => item.value === type)?.name || '-------';
        },
        show (template) {
            console.log('===> show detail disposition chat: ', template);
        },
        ...mapActions([''])
    },
    watch: {
        agtWhatsDispositionChatHistory: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
