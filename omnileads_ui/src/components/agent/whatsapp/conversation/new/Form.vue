<template>
  <div>
    <div class="card">
      <div class="grid formgrid mt-4">
        <div class="field sm:col-12 md:col-6 lg:col-6 xl:col-6">
          <label
            :class="{
              'p-error': v$.form.campaign.$invalid && submitted,
            }"
            >{{ $t("models.whatsapp.conversation.new.model.campaign") }}*</label
          >
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-sitemap"></i>
            </span>
            <Dropdown
              v-model="v$.form.campaign.$model"
              class="w-full"
              :class="{
                'p-invalid': v$.form.campaign.$invalid && submitted,
              }"
              @change="getDataByCampaign($event.value)"
              :options="campaigns"
              :filter="true"
              :showClear="true"
              placeholder="-----"
              optionLabel="name"
              optionValue="id"
              optionGroupLabel="label"
              optionGroupChildren="items"
              :emptyFilterMessage="$t('globals.without_data')"
              v-bind:filterPlaceholder="
                $t('globals.find_by', { field: $tc('globals.name') }, 1)
              "
            />
          </div>
          <small
            v-if="
              (v$.form.campaign.$invalid && submitted) ||
              v$.form.campaign.$pending.$response
            "
            class="p-error"
          >
            {{
              v$.form.campaign.required.$message.replace(
                "Value",
                $t("models.whatsapp.conversation.new.model.campaign")
              )
            }}
          </small>
        </div>
        <div class="field sm:col-12 md:col-6 lg:col-6 xl:col-6">
          <label
            :class="{
              'p-error': v$.form.template.$invalid && submitted,
            }"
            >{{ $t("models.whatsapp.conversation.new.model.template") }}*</label
          >
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-file"></i>
            </span>
            <Dropdown
              v-model="v$.form.template.$model"
              class="w-full"
              :class="{
                'p-invalid': v$.form.template.$invalid && submitted,
              }"
              :options="templates"
              :filter="true"
              :showClear="true"
              placeholder="-----"
              optionLabel="name"
              optionValue="id"
              :emptyFilterMessage="$t('globals.without_data')"
              v-bind:filterPlaceholder="
                $t('globals.find_by', { field: $tc('globals.name') }, 1)
              "
            />
          </div>
          <small
            v-if="
              (v$.form.template.$invalid && submitted) ||
              v$.form.template.$pending.$response
            "
            class="p-error"
          >
            {{
              v$.form.template.required.$message.replace(
                "Value",
                $t("models.whatsapp.conversation.new.model.template")
              )
            }}
          </small>
        </div>
        <div class="field sm:col-12 md:col-6 lg:col-6 xl:col-6">
          <label
            :class="{
              'p-error': v$.form.contact.$invalid && submitted,
            }"
            >{{ $t("models.whatsapp.conversation.new.model.contact") }}*</label
          >
          <div class="p-inputgroup mt-2">
            <span class="p-inputgroup-addon">
              <i class="pi pi-user"></i>
            </span>
            <Dropdown
              v-model="v$.form.contact.$model"
              class="w-full"
              :class="{
                'p-invalid': v$.form.contact.$invalid && submitted,
              }"
              :options="contacts"
              :filter="true"
              :showClear="true"
              placeholder="-----"
              optionLabel="phone"
              :emptyFilterMessage="$t('globals.without_data')"
              v-bind:filterPlaceholder="
                $t('globals.find_by', { field: $tc('globals.phone') }, 1)
              "
            >
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex align-items-center">
                  <div>
                    {{ getContactInfo(slotProps.value) }}
                  </div>
                </div>
                <span v-else>
                  {{ slotProps.placeholder }}
                </span>
              </template>
              <template #option="slotProps">
                <div class="flex align-items-center">
                  <div>
                    {{ getContactInfo(slotProps.option) }}
                  </div>
                </div>
              </template>
            </Dropdown>
          </div>
          <small
            v-if="
              (v$.form.contact.$invalid && submitted) ||
              v$.form.contact.$pending.$response
            "
            class="p-error"
          >
            {{
              v$.form.contact.required.$message.replace(
                "Value",
                $t("models.whatsapp.conversation.new.model.contact")
              )
            }}
          </small>
        </div>
      </div>
      <div class="flex justify-content-end flex-wrap mt-4">
        <div class="flex align-items-center">
          <Button
            class="p-button-danger p-button-outlined mr-2"
            :label="$t('globals.cancel')"
            @click="closeModal"
          />
          <Button
            :label="$t('globals.create')"
            @click="createConversation(!v$.$invalid)"
          />
        </div>
      </div>
    </div>
    <ModalTemplateParams
      :showModal="showModal"
      :template="template"
      :contactPhone="contactPhone"
      :campaignId="campaignId"
      @handleModalEvent="handleModal"
    />
  </div>
</template>

<script>
import { FilterMatchMode } from 'primevue/api';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { mapActions, mapState } from 'vuex';
import { HTTP_STATUS } from '@/globals';
import { CAMPAIGN_TYPES } from '@/globals/supervisor/campaign';
import { TEMPLATE_TYPES } from '@/globals/supervisor/whatsapp';
import { notificationEvent, NOTIFICATION } from '@/globals/agent/whatsapp';
import ModalTemplateParams from '@/components/agent/whatsapp/conversation/new/ModalTemplateParams';

export default {
    setup: () => ({ v$: useVuelidate() }),
    validations () {
        return {
            form: {
                campaign: { required },
                contact: { required },
                template: { required }
            }
        };
    },
    components: {
        ModalTemplateParams
    },
    inject: ['$helpers'],
    data () {
        return {
            form: {
                campaign: null,
                contact: null,
                template: null
            },
            submitted: false,
            filters: null,
            templates: [],
            contacts: [],
            showModal: false,
            template: null,
            campaignId: null,
            contactPhone: null,
            campaigns: [
                {
                    type: CAMPAIGN_TYPES.INBOUND,
                    label: this.$t('models.campaign.types.inbound'),
                    items: []
                },
                {
                    type: CAMPAIGN_TYPES.MANUAL,
                    label: this.$t('models.campaign.types.manual'),
                    items: []
                },
                {
                    type: CAMPAIGN_TYPES.PREVIEW,
                    label: this.$t('models.campaign.types.preview'),
                    items: []
                },
                {
                    type: CAMPAIGN_TYPES.DIALER,
                    label: this.$t('models.campaign.types.dialer'),
                    items: []
                }
            ]
        };
    },
    created () {
        this.updatedLocalStorage();
    },
    computed: {
        ...mapState([
            'supWhatsappLineCampaigns',
            'supCampaignTemplates',
            'agtWhatsContactList'
        ])
    },
    mounted () {
        window.addEventListener('storage', this.updatedLocalStorage);
        this.updatedLocalStorage();
    },
    methods: {
        ...mapActions(['initSupCampaignTemplates', 'agtWhatsContactListInit']),
        updatedLocalStorage () {
            const resetForm = localStorage.getItem('agtWhatsConversationNewResetForm') === 'true';
            if (resetForm) {
                this.initializeData();
                localStorage.setItem('agtWhatsConversationNewResetForm', false);
            }
        },
        handleModal ({
            showModal = false,
            template = null,
            campaignId = null,
            contactPhone = null,
            response = null
        }) {
            this.showModal = showModal;
            this.template = template;
            this.campaignId = campaignId;
            this.contactPhone = contactPhone;
            localStorage.setItem('agtWhatsConversationsList', true);
            if (response) {
                this.nofifyResponse(response);
            }
        },
        async nofifyResponse (response) {
            const { status, message } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                this.closeModal();
                // this.$router.push({ name: 'supervisor_whatsapp_providers' });
                await notificationEvent(
                    NOTIFICATION.TITLES.SUCCESS,
                    message,
                    NOTIFICATION.ICONS.SUCCESS
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
        },
        async getDataByCampaign (campaignId) {
            await this.getTemplatesByCampaign(campaignId);
            await this.getContactsByCampaign(campaignId);
        },
        async getTemplatesByCampaign (campaignId) {
            const campaign = this.supWhatsappLineCampaigns.find(
                (c) => c.id === campaignId
            );
            await this.initSupCampaignTemplates({
                campaignId,
                lineId: campaign.line_id
            });
        },
        async getContactsByCampaign (campaignId) {
            await this.agtWhatsContactListInit({ campaignId, conversationId: 'tes' });
        },
        getContactInfo (contact) {
            const data = JSON.parse(contact.data);
            return `${data[0]} (${contact.phone})`;
        },
        closeModal () {
            this.$emit('closeModalEvent');
        },
        initializeData () {
            this.initFormData();
            this.submitted = false;
        },
        initFormData () {
            this.form = {
                campaign: null,
                contact: null,
                template: null
            };
            this.initFilters();
        },
        clearFilter () {
            this.initFilters();
        },
        initFilters () {
            this.filters = {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS }
            };
        },
        async createConversation (isFormValid) {
            this.submitted = true;
            if (!isFormValid) {
                return null;
            }
            this.handleModal({
                showModal: true,
                template: this.templates.find((t) => t.id === this.form.template),
                campaignId: this.form.campaign,
                contactPhone: this.form.contact.phone
            });
        }
    },
    watch: {
        supWhatsappLineCampaigns: {
            handler () {
                if (this.supWhatsappLineCampaigns.length > 0) {
                    const manualCampaigns =
            this.supWhatsappLineCampaigns.filter(
                (c) => c.type === CAMPAIGN_TYPES.MANUAL
            ) || [];
                    const inboundCampaigns =
            this.supWhatsappLineCampaigns.filter(
                (c) => c.type === CAMPAIGN_TYPES.INBOUND
            ) || [];
                    const previewCampaigns =
            this.supWhatsappLineCampaigns.filter(
                (c) => c.type === CAMPAIGN_TYPES.PREVIEW
            ) || [];
                    const dialerCampaigns =
            this.supWhatsappLineCampaigns.filter(
                (c) => c.type === CAMPAIGN_TYPES.DIALER
            ) || [];
                    if (inboundCampaigns.length > 0) {
                        this.campaigns.find(
                            (c) => c.type === CAMPAIGN_TYPES.INBOUND
                        ).items = inboundCampaigns;
                    } else {
                        this.campaigns = this.campaigns.filter(
                            (c) => c.type !== CAMPAIGN_TYPES.INBOUND
                        );
                    }
                    if (manualCampaigns.length > 0) {
                        this.campaigns.find((c) => c.type === CAMPAIGN_TYPES.MANUAL).items =
              manualCampaigns;
                    } else {
                        this.campaigns = this.campaigns.filter(
                            (c) => c.type !== CAMPAIGN_TYPES.MANUAL
                        );
                    }
                    if (previewCampaigns.length > 0) {
                        this.campaigns.find(
                            (c) => c.type === CAMPAIGN_TYPES.PREVIEW
                        ).items = previewCampaigns;
                    } else {
                        this.campaigns = this.campaigns.filter(
                            (c) => c.type !== CAMPAIGN_TYPES.PREVIEW
                        );
                    }
                    if (dialerCampaigns.length > 0) {
                        this.campaigns.find((c) => c.type === CAMPAIGN_TYPES.DIALER).items =
              dialerCampaigns;
                    } else {
                        this.campaigns = this.campaigns.filter(
                            (c) => c.type !== CAMPAIGN_TYPES.DIALER
                        );
                    }
                }
            },
            deep: true,
            immediate: true
        },
        supCampaignTemplates: {
            handler () {
                if (this.supCampaignTemplates.length > 0) {
                    this.templates = this.supCampaignTemplates.filter(
                        (t) => t.type === TEMPLATE_TYPES.WHATSAPP
                    );
                } else {
                    this.templates = [];
                }
            },
            deep: true,
            immediate: true
        },
        agtWhatsContactList: {
            handler () {
                if (this.agtWhatsContactList.length > 0) {
                    this.contacts = this.agtWhatsContactList;
                } else {
                    this.contacts = [];
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
