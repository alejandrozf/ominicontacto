export default {
    initSupFacebookReportCampaignConversations (state, conversations) {
        state.supFacebookReportCampaignConversations = conversations;
    },
    initSupFacebookReportCampaignAgents (state, agents) {
        state.supFacebookReportCampaignAgents = agents.map((agent) => {
            return {
                value: agent.agent_id,
                name: agent.agent_full_name
            };
        });
    }
};
