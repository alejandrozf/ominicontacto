export default {
    ContactList: (campaignId) => `/api/v1/facebook/contact/${campaignId}`,
    ContactCreateFromConversation: (campaignId, conversationId) => `/api/v1/facebook/contact/${campaignId}/create_contact_from_conversation/${conversationId}`,
    ContactCreate: (campaignId) => `/api/v1/facebook/contact/${campaignId}`,
    ContactUpdate: (campaignId, contactId) => `/api/v1/facebook/contact/${campaignId}/${contactId}`,
    ContactCampaignDBFields: (campaignId) => `/api/v1/facebook/contact/${campaignId}/db_fields`,
    ContactSearch: (campaignId) => `/api/v1/facebook/contact/${campaignId}/search`
};
