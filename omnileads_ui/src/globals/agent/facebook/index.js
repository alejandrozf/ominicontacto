export const FACEBOOK_URL_NAME = 'agent_facebook';
export const notificationEvent = (title, text, icon) => {
    const event = new CustomEvent('onFacebookNotificationEvent', {
        detail: { title, text, icon }
    });
    window.parent.document.dispatchEvent(event);
};
export const FACEBOOK_MESSAGE = {
    SENDERS: {
        AGENT: 0,
        CLIENT: 1
    },
    STATUS: {
        SENT: 'sent',
        DELIVERED: 'delivered',
        READ: 'read',
        ERROR: 'failed'
    }
};
export const NOTIFICATION = {
    ICONS: {
        SUCCESS: 'SUCCESS',
        ERROR: 'ERROR',
        WARNING: 'WARNING',
        INFO: 'INFO'
    },
    TITLES: {
        SUCCESS: 'SUCCESS',
        ERROR: 'ERROR',
        WARNING: 'WARNING',
        FACEBOOK_NEW_CHAT: null,
        FACEBOOK_CHAT_ATTENDED: 'FACEBOOK_CHAT_ATTENDED',
        FACEBOOK_CHAT_TRANSFERED: 'FACEBOOK_CHAT_TRANSFERED',
        FACEBOOK_NEW_MESSAGE: null,
        FACEBOOK_MESSAGE_STATUS: null,
        FACEBOOK_CHAT_EXPIRED: 'FACEBOOK_CHAT_EXPIRED'
    }
};
export const FACEBOOK_EVENTS = {
    NEW_CHAT: 'facebook_new_chat',
    CHAT_ATTENDED: 'facebook_chat_attended',
    CHAT_TRANSFERED: 'facebook_chat_transfered',
    NEW_MESSAGE: 'facebook_new_message',
    MESSAGE_STATUS: 'facebook_message_status',
    CHAT_EXPIRED: 'facebook_chat_expired'
};
export const FACEBOOK_LOCALSTORAGE_EVENTS = {
    TEMPLATES_INIT_EVENT: 'facebook-localstorage-templates-init-data-event',
    CONVERSATION: {
        NEW_INIT_DATA: 'facebook-localstorage-conversation-new-init-data-event',
        DETAIL_INIT_DATA: 'facebook-localstorage-conversation-detail-init-data-event',
        RESTART_EXPIRED_CHAT: 'facebook-localstorage-conversation-restart-expired-chat-init-data-event'
    },
    CONTACT: {
        FORM_INIT_DATA: 'facebook-localstorage-contact-form-init-data-event'
    },
    DISPOSITION: {
        FORM_INIT_DATA: 'facebook-localstorage-disposition-form-init-data-event'
    },
    TRANSFER: {
        DONE: 'facebook-localstorage--transfer--done',
        FORM_INIT_DATA: 'facebook-localstorage-transfer-form-init-data-event'
    }
};
