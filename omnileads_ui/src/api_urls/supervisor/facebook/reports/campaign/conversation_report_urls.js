const BASE_ROUTE = '/api/v1/facebook/chat';

export default {
    /** url name='api_campaign_facebook_report_conversations' */
    SupFacebookReportCampaignConversations: (campaignId = null) =>
        `${BASE_ROUTE}/${campaignId}/filter_chats`,
    /** url name='api_agents_campaign' */
    SupFacebookReportCampaignAgents: (campaignId) =>
        `/api/v1/campaign/${campaignId}/agents/`
};
