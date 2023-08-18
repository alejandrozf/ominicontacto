export const WHATSAPP_URL_NAME = 'agent_whatsapp';
export const notificationEvent = (title, text, icon) => {
    const event = new CustomEvent('onWhatsappNotificationEvent', {
        detail: { title, text, icon }
    });
    window.parent.document.dispatchEvent(event);
};
export const WHATSAPP_MESSAGE = {
    SENDERS: {
        AGENT: 0,
        CLIENT: 1
    },
    STATUS: {
        SENDING: 0,
        SENT: 1,
        DELIVERED: 2,
        READ: 3,
        ERROR: 4
    }
};
export const WHATSAPP_EVENTS = {
    NEW_CHAT: 'whatsapp_new_chat',
    CHAT_ATTENDED: 'whatsapp_chat_attended',
    CHAT_TRANSFERED: 'whatsapp_chat_transfered',
    NEW_MESSAGE: 'whatsapp_new_message',
    MESSAGE_STATUS: 'whatsapp_message_status',
    CHAT_EXPIRED: 'whatsapp_chat_expired'
};
