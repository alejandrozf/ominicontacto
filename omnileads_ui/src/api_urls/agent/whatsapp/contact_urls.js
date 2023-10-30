export default {
    ContactList: (campaignId, conversationId) => `/api/v1/whatsapp/contact/${campaignId}/${conversationId}`,
    ContactCreate: (campaignId, conversationId) => `/api/v1/whatsapp/contact/${campaignId}/${conversationId}`,
    ContactUpdate: (campaignId, conversationId, contactId) => `/api/v1/whatsapp/contact/${campaignId}/${conversationId}/${contactId}`,
    ContactCampaignDBFields: (campaignId, conversationId) => `/api/v1/whatsapp/contact/${campaignId}/${conversationId}/db_fields`,
    ContactSearch: (campaignId, conversationId) => `/api/v1/whatsapp/contact/${campaignId}/${conversationId}/search`
};
