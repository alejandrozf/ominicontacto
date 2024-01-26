<template>
  <div class="card">
    <DataTable
      :value="contacts"
      :loading="loading"
      class="p-datatable-sm"
      showGridlines
      :scrollable="true"
      scrollHeight="600px"
      responsiveLayout="scroll"
      dataKey="id"
      :rows="5"
      :rowsPerPageOptions="[5, 10, 20, 50, 100]"
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
                @input="filterChanged"
                v-model="searchFilter"
                icon="pi pi-check"
                autocomplete="off"
                :placeholder="
                  $t('globals.find_by', { field: `${$tc('globals.phone')}/${$tc('globals.name')}` })
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
        :header="$t('models.whatsapp.line.nombre')"
        :sortable="true"
      ></Column>
      <Column
        field="data"
        :header="$t('models.whatsapp.line.numero')"
        :sortable="true"
      >
        <template #body="slotProps">
          {{
            slotProps?.data?.data?.length > 0
              ? slotProps?.data?.data?.join(", ")
              : "N/A"
          }}
        </template>
      </Column>
      <Column :header="$tc('globals.option', 2)" style="max-width: 10rem">
        <template #body="slotProps">
          <Button
            icon="pi pi-send"
            class="p-button-info"
            @click="identifyContact(slotProps.data)"
            v-tooltip.top="$t('globals.use')"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { HTTP_STATUS } from '@/globals';

export default {
    inject: ['$helpers'],
    props: {
        conversationInfo: {
            type: Object,
            default: () => {
                return {
                    campaignId: null
                };
            }
        }
    },
    data () {
        return {
            searchFilter: null,
            loading: false,
            contacts: []
        };
    },
    created () {},
    computed: {
        ...mapState(['agtWhatsContactSearchResults'])
    },
    methods: {
        async filterChanged (event) {
            await this.search();
        },
        clearFilter () {
            this.searchFilter = null;
            this.contacts = [];
        },
        identifyContact (contact) {
            this.$emit('selectPreviewContactEvent', contact);
        },
        async search () {
            if (!this.searchFilter || this.searchFilter.length <= 0) {
                this.contacts = [];
                return;
            }
            this.loading = true;
            const { status, message } = await this.agtWhatsContactSearch({
                campaignId: this.conversationInfo?.campaignId || null,
                conversationId: this.conversationInfo?.id || 'tes',
                filterData: {
                    phone: this.searchFilter,
                    name: this.searchFilter
                }
            });
            this.loading = false;
            if (status !== HTTP_STATUS.SUCCESS) {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        message,
                        this.$t('globals.icon_error')
                    )
                );
            }
        },
        ...mapActions(['agtWhatsContactSearch'])
    },
    watch: {
        agtWhatsContactSearchResults: {
            handler () {
                this.contacts = this.agtWhatsContactSearchResults.map((contact) => {
                    return {
                        id: contact?.id || null,
                        data: contact?.data ? JSON.parse(contact?.data) : [],
                        phone: contact?.phone || ''
                    };
                });
            },
            deep: true,
            immediate: true
        },
        conversationInfo: {
            handler () {},
            deep: true,
            immediate: true
        }
    }
};
</script>
