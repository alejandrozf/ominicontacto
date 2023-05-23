export const WHATSAPP_URL_NAME = 'agent_whatsapp';
export const notificationEvent = (title, text, icon) => {
    const event = new CustomEvent('onWhatsappNotificationEvent', {
        detail: { title, text, icon }
    });
    window.parent.document.dispatchEvent(event);
};
