import {
    notificationEvent,
    NOTIFICATION
} from '@/globals/agent/whatsapp';

const setClientInfo = (info = null) => {
    return {
        id: info && info.id ? info.id : null,
        phone: info && info.phone ? info.phone : null,
        data: info && info.data ? info.data : null,
        dispositionId: info && info.disposition ? info.disposition : null
    };
};

const setLineInfo = (info = null) => {
    return {
        id: info && info.id ? info.id : null,
        name: info && info.name ? info.name : null,
        number: info && info.number ? info.number : null
    };
};

const setFromInfo = (info = null) => {
    if (info && info.client) {
        if (info.client.data.nombre) {
            return info.client.data.nombre;
        }
    } else if (info && info.client_alias) {
        return info.client_alias;
    }
    return info.destination;
};

export default {
    agtWhatsCoversationSendMessage (state, message) {
        state.agtWhatsCoversationMessages.push(message);
    },
    agtWhatsCoversationReciveMessage (state, data = null) {
        if (!data) return;
        const messages = state.agtWhatsCoversationMessages;
        const newMessageId = data && data.message_id ? data.message_id : null;
        const alreadyExists = messages.find(m => m.id === newMessageId);
        if (!alreadyExists) {
            const itsMine = data && data.origin ? data.origin === data.line_phone : false;
            const senderName = data && data.sender && data.sender.name ? data.sender.name : null;
            const senderPhone = data && data.sender && data.sender.phone ? data.sender.phone : '------';
            const clientName = data && data.contact_data && data.contact_data.nombre ? data.contact_data.nombre : null;
            const message = {
                id: newMessageId,
                from: itsMine
                    ? `Agente (${senderName})`
                    : clientName || senderPhone,
                conversationId: data && data.chat_id ? data.chat_id : null,
                itsMine,
                message: data && data.content ? data.content : '',
                status: data && data.status ? data.status : null,
                date: data && data.timestamp ? new Date(data.timestamp) : new Date(),
                type: data && data.type ? data.type : null,
            };
            state.agtWhatsCoversationMessages.push(message);
            if (Number(localStorage.getItem('agtWhatsappConversationAttending')) !== data.chat_id) {
                notificationEvent(
                    NOTIFICATION.TITLES.WHATSAPP_NEW_MESSAGE,
                    `Mensaje Nuevo de ${clientName || senderName || senderPhone}`,
                    NOTIFICATION.ICONS.INFO
                );
            }
        }
    },
    agtWhatsConversationInitMessages (state, messages) {
        state.agtWhatsCoversationMessages = messages;
    },
    agtWhatsConversationInfoInit (state, conversation = null) {
        state.agtWhatsCoversationInfo = {
            id: conversation && conversation.id ? conversation.id : null,
            campaignId:
                conversation && conversation.campaing_id
                    ? conversation.campaing_id
                    : null,
            campaignName:
                conversation && conversation.campaing_name
                    ? conversation.campaing_name
                    : null,
            destination:
                conversation && conversation.destination
                    ? conversation.destination
                    : null,
            agent:
                conversation && conversation.agent ? conversation.agent : null,
            isActive:
                conversation && conversation.is_active
                    ? conversation.is_active
                    : null,
            isDisposition:
                conversation && conversation.is_disposition
                    ? conversation.is_disposition
                    : null,
            expire:
                conversation && conversation.expire
                    ? conversation.expire
                    : null,
            timestamp:
                conversation && conversation.timestamp
                    ? conversation.timestamp
                    : null,
            messageNumber:
                conversation && conversation.message_number
                    ? conversation.message_number
                    : null,
            photo:
                conversation && conversation.photo ? conversation.photo : null,
            client: setClientInfo(
                conversation && conversation.client ? conversation.client : null
            ),
            line: setLineInfo(
                conversation && conversation.line ? conversation.line : null
            ),
            error:
                conversation && conversation.error ? conversation.error : false,
            errorEx:
                conversation && conversation.error_ex ? conversation.error_ex : null,
            client_alias:
                conversation && conversation.client_alias ? conversation.client_alias : null
        };
    },
    agtWhatsChatsListInit (state, { isNew, inProgress }) {
        const chats = [];
        isNew.forEach((e = null) => {
            if (e) {
                chats.push({
                    id: e.id ? e.id : null,
                    from: setFromInfo(e),
                    campaignId: e.campaing_id ? e.campaing_id : null,
                    campaignName: e.campaing_name ? e.campaing_name : '-------',
                    numMessages: e.message_number ? e.message_number : 0,
                    photo: e.photo ? e.photo : '',
                    isNew: true,
                    isMine: false,
                    answered: false,
                    date: e.timestamp ? new Date(e.timestamp) : null,
                    expire: e.expire ? new Date(e.expire) : null,
                    errorEx: e.error_ex ? e.error_ex : null,
                    error: e.error ? e.error : false
                });
            }
        });
        inProgress.forEach((e = null) => {
            if (e) {
                chats.push({
                    id: e.id ? e.id : null,
                    from: setFromInfo(e),
                    campaignId: e.campaing_id ? e.campaing_id : null,
                    campaignName: e.campaing_name ? e.campaing_name : '-------',
                    numMessages: e.message_number ? e.message_number : 0,
                    photo: e.photo,
                    isNew: false,
                    isMine: true,
                    answered: false,
                    date: e.timestamp ? new Date(e.timestamp) : null,
                    expire: e.expire ? new Date(e.expire) : null,
                    errorEx: e.error_ex ? e.error_ex : null,
                    error: e.error ? e.error : false
                });
            }
        });
        state.agtWhatsChatsList = chats;
    },
    agtWhatsReceiveNewChat (state, chat = null) {
        const from = chat && chat.from ? chat.from : null;
        const contactData = chat && chat.contact_data && chat.contact_data.nombre ? chat.contact_data.nombre : null;
        state.agtWhatsChatsList.push({
            id: chat && chat.chat_id ? chat.chat_id : null,
            from: contactData || from,
            campaignId: chat && chat.campaing_id ? chat.campaing_id : null,
            campaignName: chat && chat.campaing_name ? chat.campaing_name : '-------',
            numMessages:
                chat && chat.number_messages ? chat.number_messages : 1,
            photo: chat && chat.photo ? chat.photo : '',
            isNew: true,
            isMine: false,
            answered: false,
            date: chat && chat.timestamp ? new Date(chat.timestamp) : new Date(),
            expire: chat && chat.expire ? new Date(chat.expire) : null,
            errorEx: chat && chat.error_ex ? chat.error_ex : null,
            error: chat && chat.error ? chat.error : false
        });
    },
    agtWhatsSetCoversationInfo (state, conversation = null) {
        state.agtWhatsCoversationInfo = {
            id: conversation && conversation.id ? conversation.id : null,
            campaignId:
                conversation && conversation.campaignId
                    ? conversation.campaignId
                    : null,
            campaignName:
                conversation && conversation.campaignName
                    ? conversation.campaignName
                    : null,
            destination:
                conversation && conversation.destination
                    ? conversation.destination
                    : null,
            client: setClientInfo(
                conversation && conversation.client ? conversation.client : null
            ),
            agent:
                conversation && conversation.agent ? conversation.agent : null,
            isActive:
                conversation && conversation.isActive
                    ? conversation.isActive
                    : null,
            isDisposition:
                conversation && conversation.isDisposition
                    ? conversation.isDisposition
                    : null,
            expire:
                conversation && conversation.expire
                    ? conversation.expire
                    : null,
            timestamp:
                conversation && conversation.timestamp
                    ? conversation.timestamp
                    : null,
            messageNumber:
                conversation && conversation.messageNumber
                    ? conversation.messageNumber
                    : null,
            photo:
                conversation && conversation.photo ? conversation.photo : null,
            line: setLineInfo(
                conversation && conversation.line ? conversation.line : null
            ),
            errorEx:
                conversation && conversation.errorEx ? conversation.errorEx : null,
            error:
                conversation && conversation.error ? conversation.error : false
        };
    },
    agtWhatsRestartExpiredCoversation (state, info = null) {
        if (info) {
            state.agtWhatsCoversationInfo.expire = info.expire;
            localStorage.setItem(
                'agtWhatsCoversationInfo',
                JSON.stringify(state.agtWhatsCoversationInfo)
            );
        }
    }
};
