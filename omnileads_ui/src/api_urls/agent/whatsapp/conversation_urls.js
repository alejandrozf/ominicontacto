export default {
    ChatMessages: (chatId) => `/api/v1/whatsapp/chat/${chatId}/messages`,
    ChatSendTextMessage: (chatId) => `/api/v1/whatsapp/chat/${chatId}/send_message_text`,
    ChatSendAttachmentMessage: (chatId) => `/api/v1/whatsapp/chat/${chatId}/send_message_attachment`,
    ChatAgentConversationsList: () => `/api/v1/whatsapp/chat`,
    ChatAgentConversationsDetail: (chatId) => `/api/v1/whatsapp/chat/${chatId}`
};
