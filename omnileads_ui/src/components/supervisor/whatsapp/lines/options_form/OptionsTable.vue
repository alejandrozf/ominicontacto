<template>
  <div class="card">
    <DataTable
      :value="supWhatsappLineOptions"
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
              v-if="supWhatsappLineOptions.length < maxOptions"
              type="button"
              icon="pi pi-plus"
              class="p-button-info ml-2"
              @click="newOption()"
            />
          </div>
        </div>
      </template>
      <template #empty> {{ $t("globals.without_data") }} </template>
      <template #loading> {{ $t("globals.load_info") }} </template>
      <Column
        field="value"
        :header="$t('models.whatsapp.line.options.value')"
        :sortable="true"
      ></Column>
      <Column
        field="description"
        :header="$t('models.whatsapp.line.options.description')"
      ></Column>
      <Column
        field="destinationType"
        :header="$t('models.whatsapp.line.options.destination_type')"
      >
        <template #body="slotProps">
          {{ getDestinationType(slotProps.data.destinationType) }}
        </template>
      </Column>
      <Column
        field="destination"
        :header="$t('models.whatsapp.line.options.destination')"
        :sortable="true"
      >
        <template #body="slotProps">
          {{ getDestination(slotProps.data.destination) }}
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
            @click="remove(slotProps.data.index)"
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
import { DESTINATION_OPTION_TYPES } from '@/globals/supervisor/whatsapp/line';

export default {
    inject: ['$helpers'],
    data () {
        return {
            filters: null,
            destinationTypes: [
                { name: '-------', value: null },
                {
                    name: this.$t('forms.whatsapp.line.destination_types.campaign'),
                    value: DESTINATION_OPTION_TYPES.CAMPAIGN
                }
            ],
            maxOptions: 10
        };
    },
    created () {
        this.initFilters();
    },
    computed: {
        ...mapState(['supWhatsappLineOptions', 'supWhatsappLineCampaigns'])
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
        getDestination (id) {
            const campaign = this.supWhatsappLineCampaigns.find((c) => c.id === id);
            if (campaign) {
                return `${campaign.name} (${campaign.id})`;
            } else {
                return '----------';
            }
        },
        getDestinationType (type) {
            const destinationType = this.destinationTypes.find((dt) => dt.value === type);
            if (destinationType) {
                return destinationType.name;
            } else {
                return '----------';
            }
        },
        newOption () {
            this.initWhatsappLineOptionForm();
            this.$emit('handleModalEvent', {
                showModal: true,
                formToCreate: true
            });
        },
        edit (option) {
            this.$emit('handleModalEvent', {
                showModal: true,
                formToCreate: false,
                option
            });
        },
        remove (id) {
            this.deleteWhatsappLineOption({ id });
            this.$swal(
                this.$helpers.getToasConfig(
                    this.$t('globals.success_notification'),
                    this.$t('forms.whatsapp.line.options.success_delete'),
                    this.$t('globals.icon_success')
                )
            );
        },
        ...mapActions([
            'deleteWhatsappLineOption',
            'initWhatsappLineOptionForm'
        ])
    },
    watch: {
        supWhatsappLineOptions: {
            handler () {},
            deep: true,
            immediate: true
        },
        supWhatsappLineCampaigns: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
