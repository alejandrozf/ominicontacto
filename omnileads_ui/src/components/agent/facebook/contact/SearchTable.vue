<template>
  <div class="card">
    <div
      v-if="suggestedPageClientId"
      class="mb-3 p-2 border-round surface-100 text-sm"
    >
      Podés buscar por nombre, teléfono o page_client_id. Se sugiere una coincidencia por
      <b>page_client_id</b>: <b>{{ suggestedPageClientId }}</b>.
    </div>
    <div
      v-if="suggestedContact"
      class="mb-3 p-3 border-round surface-50 border-1 border-primary"
    >
      <div class="flex justify-content-between align-items-center gap-3 flex-wrap">
        <div>
          <div class="font-semibold mb-1">Coincidencia sugerida</div>
          <div>{{ getContactData(suggestedContact.data) }}</div>
          <small class="block mt-1">
            Tel: {{ suggestedContact.phone || 'N/A' }} |
            page_client_id: {{ suggestedContact.page_client_id || 'N/A' }}
          </small>
        </div>
        <Button
          icon="pi pi-send"
          class="p-button-info"
          @click="identifyContact(suggestedContact)"
          v-tooltip.top="$t('globals.use')"
        />
      </div>
    </div>
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
                  $t('globals.find_by', { field: `${$tc('globals.phone')}/${$tc('globals.name')}/page_client_id` })
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
        :header="$tc('globals.phone')"
        :sortable="true"
      ></Column>
      <Column
        field="data"
        :header="$tc('globals.name', 1)"
        :sortable="true"
      >
        <template #body="slotProps">
          {{
            getContactData(slotProps?.data?.data)
          }}
        </template>
      </Column>
      <Column
        field="page_client_id"
        :header="'page_client_id'"
        :sortable="true"
      >
        <template #body="slotProps">
          <div class="flex align-items-center gap-2">
            <span>{{ slotProps?.data?.page_client_id || "N/A" }}</span>
            <span
              v-if="slotProps?.data?.is_suggested_match"
              class="p-tag p-tag-info"
            >
              Match sugerido
            </span>
          </div>
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
            contacts: [],
            suggestedPageClientId: null,
            suggestedContact: null,
            debounceTimer: null
        };
    },
    computed: {
        ...mapState(['agtFacebookContactSearchResults'])
    },
    methods: {
        getContactData (data = {}) {
            const values = Array.isArray(data) ? data : Object.values(data || {});
            return values.length > 0
                ? values.filter((value) => value !== null && value !== undefined && value !== '')
                    .join(', ')
                : 'N/A';
        },
        clearFilter () {
            this.searchFilter = null;
            this.contacts = [];
        },
        async loadSuggestedMatch () {
            const { status, data, message } = await this.agtFacebookContactSuggestMatch({
                campaignId: this.conversationInfo?.campaignId || null,
                conversationId: this.conversationInfo?.id || null
            });
            if (status !== HTTP_STATUS.SUCCESS) {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.error_notification'),
                        message,
                        this.$t('globals.icon_error')
                    )
                );
                return;
            }
            this.suggestedContact = data
                ? {
                    id: data?.id || null,
                    data: data?.data || {},
                    phone: data?.phone || '',
                    page_client_id: data?.page_client_id || '',
                    is_suggested_match: true
                }
                : null;
        },
        identifyContact (contact) {
            this.$emit('selectPreviewContactEvent', contact);
        },
        filterChanged () {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.search();
            }, 350);
        },
        async search () {
            if (!this.searchFilter || this.searchFilter.trim().length < 2) {
                this.contacts = [];
                return;
            }
            this.loading = true;
            const { status, message } = await this.agtFacebookContactSearch({
                campaignId: this.conversationInfo?.campaignId || null,
                filterData: {
                    search: this.searchFilter,
                    phone: this.searchFilter,
                    name: this.searchFilter,
                    conversation_id: this.conversationInfo?.id || null,
                    limit: 20
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
        ...mapActions(['agtFacebookContactSearch', 'agtFacebookContactSuggestMatch'])
    },
    watch: {
        agtFacebookContactSearchResults: {
            handler () {
                this.contacts = this.agtFacebookContactSearchResults.map((contact) => {
                    return {
                        id: contact?.id || null,
                        data: contact?.data || {},
                        phone: contact?.phone || '',
                        page_client_id: contact?.page_client_id || '',
                        is_suggested_match:
                            !!this.suggestedPageClientId &&
                            contact?.page_client_id === this.suggestedPageClientId
                    };
                }).sort((left, right) => {
                    return Number(right.is_suggested_match) - Number(left.is_suggested_match);
                });
            },
            deep: true,
            immediate: true
        },
        conversationInfo: {
            async handler () {
                this.suggestedPageClientId = this.conversationInfo?.page_client_id || null;
                this.suggestedContact = null;
                if (this.suggestedPageClientId && this.conversationInfo?.id && this.conversationInfo?.campaignId) {
                    await this.loadSuggestedMatch();
                }
            },
            deep: true,
            immediate: true
        }
    },
    beforeUnmount () {
        clearTimeout(this.debounceTimer);
    }
};
</script>
