const BASE_ROUTE = '/api/v1/whatsapp/disposition_chat';

export default {
    DispositionChatDetail: (id) => `${BASE_ROUTE}/${id}`,
    DispositionChatUpdate: (id) => `${BASE_ROUTE}/${id}`,
    DispositionChatCreate: () => `${BASE_ROUTE}`,
    DispositionChatHistory: (id) => `${BASE_ROUTE}/${id}/history`,
    DispositionChatOptions: (campaignId) => `${BASE_ROUTE}/options/${campaignId}`
};
