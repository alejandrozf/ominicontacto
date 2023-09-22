export default {
    ChatMessages: (chatId) => `/api/v1/whatsapp/chat/${chatId}/messages`,
    ChatSendTextMessage: (chatId) => `/api/v1/whatsapp/chat/${chatId}/send_message_text`,
    ChatSendAttachmentMessage: (chatId) => `/api/v1/whatsapp/chat/${chatId}/send_message_attachment`,
    ChatSendTemplateMessage: (chatId) => `/api/v1/whatsapp/chat/${chatId}/send_message_template`,
    ChatSendWhatsappTemplateMessage: (chatId) => `/api/v1/whatsapp/chat/${chatId}/send_message_whatsapp_template`,
    ChatAgentConversationsList: () => `/api/v1/whatsapp/chat`,
    ChatAgentConversationsDetail: (chatId) => `/api/v1/whatsapp/chat/${chatId}`,
    ChatAgentConversationRequest: (chatId) => `/api/v1/whatsapp/chat/${chatId}/attend_chat`
};
