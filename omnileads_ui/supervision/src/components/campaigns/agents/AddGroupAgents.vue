<template>
  <div>
    <div class="field col-12">
      <Dropdown
        v-model="selectedGroup"
        class="w-full"
        :options="groupsSelectize"
        optionLabel="group"
        :placeholder="
          $t('globals.select_type', { type: $tc('globals.group', 1) }, 2)
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
        @click="addGroup"
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
            groupsSelectize: [],
            selectedGroup: null
        };
    },
    methods: {
        addGroup () {
            if (this.selectedGroup) {
                const groupId = this.selectedGroup.value;
                const group = this.groups.find((group) => groupId === group.group.id);
                const existingAgents = [];
                group.agents.forEach((agent) => {
                    if (
                        this.agents_by_campaign.find((a) => a.agent_id === agent.agent_id)
                    ) {
                        existingAgents.push(agent.agent_username);
                    } else {
                        this.addAgentToCampaign(agent);
                    }
                });
                this.selectedGroup = null;
                if (existingAgents.length > 0) {
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.warning_notification'),
                            this.$t(
                                'views.add_agents_to_campaign.already_agents_in_campaign',
                                { agents: existingAgents.join(' - ') }
                            ),
                            this.$t('globals.icon_warning'),
                            this.$t('views.add_agents_to_campaign.how_to_update')
                        )
                    );
                } else {
                    this.$swal(
                        this.$helpers.getToasConfig(
                            this.$t('globals.success_notification'),
                            this.$tc('globals.success_added_type', {
                                type: this.$tc('globals.group')
                            }),
                            this.$t('globals.icon_success'),
                            this.$t('views.add_agents_to_campaign.how_to_update')
                        )
                    );
                }
            } else {
                this.$swal(
                    this.$helpers.getToasConfig(
                        this.$t('globals.warning_notification'),
                        this.$tc('globals.not_select_type', {
                            type: this.$tc('globals.group')
                        }),
                        this.$t('globals.icon_warning')
                    )
                );
            }
        },
        updatedGroupsSelectize () {
            this.groupsSelectize = this.groups.map((group) => {
                return {
                    group: group.group.name,
                    value: group.group.id
                };
            });
        },
        ...mapActions(['addAgentToCampaign'])
    },
    watch: {
        agents_by_campaign: {
            deep: true,
            handler () {}
        },
        groups: {
            deep: true,
            handler () {
                this.updatedGroupsSelectize();
            }
        }
    },
    computed: {
        ...mapGetters({
            agents_by_campaign: 'getAgentsByCampaign',
            groups: 'getGroups'
        })
    }
};
</script>
