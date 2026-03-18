export default {
    agentList: (campaingId) => `/api/v1/whatsapp/transfer/${campaingId}/agents`,
    campaignList: (conversationId) => `/api/v1/whatsapp/transfer/${conversationId}/campaigns`,
    transferToagent: () => `/api/v1/whatsapp/transfer/to_agent`,
    transferToCampaign: () => `/api/v1/whatsapp/transfer/to_campaign`
};
