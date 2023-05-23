<template>
  <div class="card">
    <DataTable
      :value="agtWhatsManagements"
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
      :globalFilterFields="['phone']"
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
        field="phone"
        style="max-width: 15rem"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.phone')"
      >
        <template #body="slotProps">
          {{ phoneFormat(slotProps.data.phone) }}
        </template>
      </Column>
      <Column
        field="agent"
        style="max-width: 15rem"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.agent')"
      >
        <template #body="slotProps">
          {{ getAgent(slotProps.data.agent) }}
        </template>
      </Column>
      <Column
        field="start_datetime"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.start_datetime')"
      >
        <template #body="slotProps">
          {{ timeFormat(slotProps.data.start_datetime) }}
        </template>
      </Column>
      <Column
        field="end_datetime"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.end_datetime')"
      >
        <template #body="slotProps">
          {{ timeFormat(slotProps.data.end_datetime) }}
        </template>
      </Column>
      <Column
        field="type"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.type')"
      >
        <template #body="slotProps">
          <Tag :value="getType(slotProps.data.type)" rounded></Tag>
        </template>
      </Column>
      <Column
        field="mean"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.mean')"
      >
        <template #body="slotProps">
          <Tag :value="getMean(slotProps.data.mean)" rounded></Tag>
        </template>
      </Column>
      <Column
        field="result"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.result')"
      >
        <template #body="slotProps">
          <Tag :value="getResult(slotProps.data.result)" rounded></Tag>
        </template>
      </Column>
      <Column
        field="score"
        :sortable="true"
        :header="$t('models.whatsapp.disposition_form.score')"
      >
        <template #body="slotProps">
          <Tag :value="getScore(slotProps.data.score)" rounded></Tag>
        </template>
      </Column>
      <Column :header="$tc('globals.option', 2)" style="max-width: 10rem">
        <template #body="slotProps">
          <Button
            icon="pi pi-eye"
            class="p-button-secondary"
            @click="show(slotProps.data)"
            v-tooltip.top="$t('globals.show')"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { FilterMatchMode } from 'primevue/api';
import {
    RESULTS,
    TYPES,
    SCORES,
    MEANS
} from '@/globals/agent/whatsapp/disposition';

export default {
    inject: ['$helpers'],
    data () {
        return {
            filters: null,
            tipos: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.provider.types.twilio'),
                    value: TYPES.OPT1
                }
            ],
            medios: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.provider.types.twilio'),
                    value: MEANS.OPT1
                }
            ],
            resultados: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.provider.types.twilio'),
                    value: RESULTS.OPT1
                }
            ],
            calificaciones: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.provider.types.twilio'),
                    value: SCORES.OPT1
                }
            ]
        };
    },
    created () {
        this.initFilters();
        this.agtWhatsTemplatesInit();
    },
    computed: {
        ...mapState(['agtWhatsManagements', 'agtWhatsManagementAgents'])
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
        getType (type) {
            return this.tipos.find((t) => t.value === type)?.name;
        },
        getMean (type) {
            return this.medios.find((t) => t.value === type)?.name;
        },
        getResult (type) {
            return this.resultados.find((t) => t.value === type)?.name;
        },
        getScore (type) {
            return this.calificaciones.find((t) => t.value === type)?.name;
        },
        getAgent (agent) {
            return this.agtWhatsManagementAgents.find((a) => a.agent_id === agent)
                ?.agent_full_name;
        },
        show (template) {
            this.agtWhatsTemplateSendMsg(template);
        },
        ...mapActions(['agtWhatsTemplatesInit', 'agtWhatsTemplateSendMsg'])
    },
    watch: {
        agtWhatsManagements: {
            handler () {},
            deep: true,
            immediate: true
        },
        agtWhatsManagementAgents: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
