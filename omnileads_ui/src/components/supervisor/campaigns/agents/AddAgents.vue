<template>
  <div>
    <div class="field col-12">
      <Dropdown
        v-model="selectedAgent"
        class="w-full"
        :options="agents"
        optionLabel="agent"
        :placeholder="
          $t('globals.select_type', { type: $tc('globals.agent', 1) }, 2)
        "
        :emptyFilterMessage="$t('globals.without_data')"
        :filter="true"
        v-bind:filterPlaceholder="
          $t('globals.find_by', { field: $tc('globals.name') }, 1)
        "
      />
    </div>
    <div class="field col-4">
      <Button
        type="button"
        class="p-button"
        v-bind:label="$t('globals.add')"
        @click="addAgent"
      />
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

export default {
    inject: ['$helpers'],
    data () {
        return {
            selectedAgent: null,
            agents: []
        };
    },
    methods: {
        updateAgentsDisplay () {
            const agentsCampaignIds = this.agents_by_campaign.map(
                (agent) => agent.agent_id
            );
            const activeAgentsFilter = this.active_agents.filter(
                (agent) => !agentsCampaignIds.includes(agent.agent_id)
            );
            this.agents = activeAgentsFilter.map((agent) => {
                return {
                    agent: agent.agent_full_name,
                    value: agent.agent_id
                };
            });
        },
        addAgent () {
            if (this.selectedAgent) {
                const agentId = this.selectedAgent.value;
                if (
                    this.agents_by_campaign.find((agent) => agentId === agent.agent_id)
                ) {
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.warning_notification'),
                            this.$t('views.add_agents_to_campaign.already_agent_in_campaign'),
                            this.$t('globals.icon_warning')
                        )
                    );
                } else {
                    const agent = this.active_agents.find(
                        (agent) => agentId === agent.agent_id
                    );
                    this.addAgentToCampaign(agent);
                    this.selectedAgent = null;
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.success_notification'),
                            this.$tc('globals.success_added_type', {
                                type: this.$tc('globals.agent')
                            }),
                            this.$t('globals.icon_success'),
                            this.$t('globals.how_to_save_changes')
                        )
                    );
                }
            } else {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.warning_notification'),
                        this.$tc('globals.not_select_type', {
                            type: this.$tc('globals.agent')
                        }),
                        this.$t('globals.icon_warning')
                    )
                );
            }
        },
        ...mapActions(['addAgentToCampaign'])
    },
    watch: {
        agents_by_campaign: {
            handler () {
                this.updateAgentsDisplay();
            }
        },
        active_agents: {
            handler () {
                this.updateAgentsDisplay();
            }
        }
    },
    computed: {
        ...mapGetters({
            agents_by_campaign: 'getAgentsByCampaign',
            active_agents: 'getActiveAgents'
        })
    }
};
</script>
