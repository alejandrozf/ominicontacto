const BASE_ROUTE = '/api/v1/whatsapp/chat';

export default {
    SupWhatsReportCampaignConversations: (campaignId = null) =>
        `${BASE_ROUTE}/${campaignId}/filter_chats`,
    SupWhatsReportCampaignAgents: (campaignId) =>
        `/api/v1/campaign/${campaignId}/agents/`
};
