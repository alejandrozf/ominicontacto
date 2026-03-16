const BASE_ROUTE = '/api/v1/facebook/chat';

export default {
    SupFacebookReportCampaignConversations: (campaignId = null) =>
        `${BASE_ROUTE}/${campaignId}/filter_chats`,
    SupFacebookReportCampaignAgents: (campaignId) =>
        `/api/v1/campaign/${campaignId}/agents/`
};
