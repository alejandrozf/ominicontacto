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
