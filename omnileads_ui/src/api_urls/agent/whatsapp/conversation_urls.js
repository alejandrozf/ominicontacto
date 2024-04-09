const BASE_ROUTE = '/api/v1/whatsapp/chat';

export default {
    ChatMessages: (chatId) => `${BASE_ROUTE}/${chatId}/messages`,
    ChatSendTextMessage: (chatId) => `${BASE_ROUTE}/${chatId}/send_message_text`,
    ChatSendAttachmentMessage: (chatId) => `${BASE_ROUTE}/${chatId}/send_message_attachment`,
    ChatSendTemplateMessage: (chatId) => `${BASE_ROUTE}/${chatId}/send_message_template`,
    ChatSendWhatsappTemplateMessage: (chatId) => `${BASE_ROUTE}/${chatId}/send_message_whatsapp_template`,
    ChatAgentReactiveExpiredConversation: (chatId) => `${BASE_ROUTE}/${chatId}/reactive_expired_conversation`,
    ChatAgentConversationsList: () => `${BASE_ROUTE}`,
    ChatAgentConversationsDetail: (chatId) => `${BASE_ROUTE}/${chatId}`,
    ChatAgentConversationRequest: (chatId) => `${BASE_ROUTE}/${chatId}/attend_chat`,
    ChatAgentNewConversation: () => `${BASE_ROUTE}/send_initing_conversation`
};
