export default {
    initSupWhatsReportCampaignConversations (state, conversations) {
        state.supWhatsReportCampaignConversations = conversations;
    },
    initSupWhatsReportCampaignAgents (state, agents) {
        state.supWhatsReportCampaignAgents = agents.map((agent) => {
            return {
                value: agent.agent_id,
                name: agent.agent_full_name
            };
        });
    }
};
