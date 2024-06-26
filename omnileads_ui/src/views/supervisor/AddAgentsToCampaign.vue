<template>
  <div class="card">
    <h1>{{ $t("globals.campaign_info", { name: campaign["nombre"] }) }}</h1>
    <div class="formgrid grid">
      <div class="field col-6">
        <h2>{{ $tc("globals.agent", 2) }}</h2>
        <AddAgents />
      </div>
      <div class="field col-6">
        <h2>{{ $tc("globals.group", 2) }}</h2>
        <AddGroupAgents />
      </div>
    </div>
    <hr />
    <div class="grid mt-5">
      <div class="field col-12">
        <div class="flex justify-content-between flex-wrap">
          <div class="flex align-items-center justify-content-center">
            <h2>{{ $t("views.add_agents_to_campaign.agents_campaign") }}</h2>
          </div>
          <div class="flex align-items-center justify-content-center">
            <Button
              class="mr-2 p-button-info p-button-rounded"
              icon="pi pi-info-circle"
              v-tooltip.left="
                $t('views.add_agents_to_campaign.how_to_edit_penalty')
              "
            />
            <Button
              type="button"
              :label="$t('globals.save')"
              class="mr-2 p-button"
              :disabled="btnStatusSave"
              icon="pi pi-save"
              @click="updateAgents()"
            />
          </div>
        </div>
        <AgentsCampaignTable />
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import AddAgents from '@/components/supervisor/campaigns/agents/AddAgents.vue';
import AddGroupAgents from '@/components/supervisor/campaigns/agents/AddGroupAgents.vue';
import AgentsCampaignTable from '@/components/supervisor/campaigns/agents/AgentsCampaignTable.vue';
import AgentsCampaignService from '@/services/supervisor/agents_campaign_service';
import { CONFIRM_BTN_COLOR, CANCEL_BTN_COLOR } from '@/globals';

export default {
    name: 'AddAgentsToCampaign',
    components: {
        AgentsCampaignTable,
        AddGroupAgents,
        AddAgents
    },
    inject: ['$helpers'],
    data () {
        return {
            campaignId: null,
            btnStatusSave: false
        };
    },
    async created () {
        const element = window.parent.document.getElementById(
            'add_agents_to_campaign'
        );
        this.campaignId = element.value;
        this.agentsCampaignService = new AgentsCampaignService();
        await this.initAgentsCampaign(this.campaignId);
        await this.initActiveAgents();
    },
    methods: {
        ...mapActions(['initAgentsCampaign', 'initActiveAgents']),
        async updateAgents () {
            const agents = await this.agents_by_campaign.map((agent) => {
                return {
                    agent_id: agent.agent_id,
                    agent_penalty: agent.agent_penalty
                };
            });
            if (this.agents_by_campaign.length === 0) {
                this.$swal({
                    title: this.$t('globals.sure_notification'),
                    text: this.$t('views.add_agents_to_campaign.empty_campaign_notice'),
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
                        const { status, ok } =
              await this.agentsCampaignService.updateAgentsByCampaign({
                  campaign_id: this.campaignId,
                  agents
              });
                        this.$swal.close();
                        if (status === 200 && ok === true) {
                            await this.initAgentsCampaign(this.campaignId);
                            await this.initActiveAgents();
                            this.$swal(
                                this.$helpers.getToasConfig(
                                    this.$t('globals.success_notification'),
                                    this.$tc('globals.success_updated_type', {
                                        type: this.$tc('globals.agent', 2)
                                    }),
                                    this.$t('globals.icon_success')
                                )
                            );
                        } else {
                            this.$swal(
                                this.$helpers.getToasConfig(
                                    this.$t('globals.error_notification'),
                                    this.$tc('globals.error_to_updated', {
                                        type: this.$tc('globals.agent', 2)
                                    }),
                                    this.$t('globals.icon_error')
                                )
                            );
                        }
                        this.btnStatusSave = false;
                    } else if (result.dismiss === this.$swal.DismissReason.cancel) {
                        this.$swal(
                            this.$helpers.getToasConfig(
                                this.$t('globals.cancelled'),
                                this.$t('views.add_agents_to_campaign.agents_not_save'),
                                this.$t('globals.icon_error')
                            )
                        );
                    }
                });
            } else {
                this.btnStatusSave = true;
                this.$swal.fire({
                    title: this.$t('globals.processing_request'),
                    timerProgressBar: true,
                    allowOutsideClick: false,
                    didOpen: () => {
                        this.$swal.showLoading();
                    }
                });
                const { status, ok } =
          await this.agentsCampaignService.updateAgentsByCampaign({
              campaign_id: this.campaignId,
              agents
          });
                this.$swal.close();
                if (status === 200 && ok === true) {
                    await this.initAgentsCampaign(this.campaignId);
                    await this.initActiveAgents();
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.success_notification'),
                            this.$tc('globals.success_updated_type', {
                                type: this.$tc('globals.agent', 2)
                            }),
                            this.$t('globals.icon_success')
                        )
                    );
                } else {
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.error_notification'),
                            this.$tc('globals.error_to_updated', {
                                type: this.$tc('globals.agent', 2)
                            }),
                            this.$t('globals.icon_error')
                        )
                    );
                }
                this.btnStatusSave = false;
            }
        }
    },
    computed: {
        ...mapState(['campaign', 'agents_by_campaign'])
    }
};
</script>
