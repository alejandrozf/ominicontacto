import {
    notificationEvent,
    NOTIFICATION
} from '@/globals/agent/facebook';

const setClientInfo = (info = null) => {
    return {
        id: info && info.id ? info.id : null,
        phone: info && info.phone ? info.phone : null,
        page_client_id: info && info.page_client_id ? info.page_client_id : null,
        data: info && info.data ? info.data : null,
        dispositionId: info && info.disposition ? info.disposition : null
    };
};

const setPageInfo = (info = null) => {
    return {
        id: info && info.id ? info.id : null,
        name: info && info.name ? info.name : null,
        page_id: info && info.page_id ? info.page_id : null
    };
};

const setFromInfo = (info = null) => {
    if (info && info.client) {
        if (info.client.data.nombre) {
            return info.client.data.nombre;
        }
        if (info.client.data.name) {
            return info.client.data.name;
        }
    } else if (info && info.client_alias) {
        return info.client_alias;
    }
    return info.destination;
};

export default {
    agtFacebookConversationSendMessage (state, message) {
        state.agtFacebookConversationMessages.push(message);
    },
    agtFacebookConversationSendTemplateMessage (state, messages) {
        state.agtFacebookConversationMessages = [...messages];
    },
    agtFacebookConversationReciveMessage (state, data = null) {
        if (!data) return;
        const messages = state.agtFacebookConversationMessages;
        const newMessageId = data && data.message_id ? data.message_id : null;
        const alreadyExists = messages.find(m => m.id === newMessageId);
        if (!alreadyExists) {
            const itsMine = data && data.origin ? data.origin === data.page_id : false;
            const senderName = data && data.sender && data.sender.name ? data.sender.name : null;
            const senderPhone = data && data.sender && data.sender.phone ? data.sender.phone : '------';
            var clientName = '-';
            if (data && data.contact_data) {
                if (data.contact_data.nombre) {
                    clientName = data.contact_data.nombre;
                }
                else if (data.contact_data.name) {
                    clientName = data.contact_data.name;
                }
            }
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
            if (Number(localStorage.getItem('agtFacebookConversationAttending')) !== data.chat_id) {
                notificationEvent(
                    NOTIFICATION.TITLES.FACEBOOK_NEW_MESSAGE,
                    `Mensaje Nuevo de ${clientName || senderName || senderPhone}`,
                    NOTIFICATION.ICONS.INFO
                );
                var a =state.agtFacebookChatsList.find(m => m.id === data.chat_id);
                a.numMessagesUnread = a.numMessagesUnread + 1
                console.log("*******", a.numMessagesUnread)

            }
            else{
                state.agtFacebookConversationMessages.push(message);
            }
        }
    },
    agtFacebookConversationInitMessages(state, messages) {
        console.log('agtFacebookConversationInitMessages >>', messages);
        // Reemplazamos el array completo para que Vue detecte cambios
        state.agtFacebookConversationMessages = [...messages];
    },
    agtFacebookConversationInfoInit (state, conversation = null) {
        console.log("agtFacebookConversationInfoInit >>", conversation);
        state.agtFacebookConversationInfo = {
            id: conversation && conversation.id ? conversation.id : null,
            campaignId:
                conversation && conversation.campaing_id
                    ? conversation.campaing_id
                    : null,
            campaignName:
                conversation && conversation.campaing_name
                    ? conversation.campaing_name
                    : null,
            page_client_id:
                conversation && conversation.destination
                    ? conversation.destination
                    : null,
            agent:
                conversation && conversation.agent ? conversation.agent : null,
            transferAgent:
                conversation && conversation.transfer_agent
                    ? conversation.transfer_agent
                    : null,
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
            messageUnreadNumber:
                    conversation && conversation.message_unread
                        ? conversation.message_unread
                        : null,
            photo:
                conversation && conversation.photo ? conversation.photo : null,
            client: setClientInfo(
                conversation && conversation.client ? conversation.client : null
            ),
            page: setPageInfo(
                conversation && conversation.page ? conversation.page : null
            ),
            error:
                conversation && conversation.error ? conversation.error : false,
            errorEx:
                conversation && conversation.error_ex ? conversation.error_ex : null,
            client_alias:
                conversation && conversation.client_alias ? conversation.client_alias : null
        };
        console.log('agtFacebookConversationInfo ******', state.agtFacebookConversationInfo);
    },
    agtFacebookChatsListInit (state, { isNew, inProgress }) {
        const chats = [];
        isNew.forEach((e = null) => {
            if (e) {
                chats.push({
                    id: e.id ? e.id : null,
                    from: setFromInfo(e),
                    campaignId: e.campaing_id ? e.campaing_id : null,
                    campaignName: e.campaing_name ? e.campaing_name : '-------',
                    numMessages: e.message_number ? e.message_number : 0,
                    numMessagesUnread: e.message_unread ? e.message_unread : 0,
                    photo: e.photo ? e.photo : '',
                    isNew: true,
                    isMine: false,
                    answered: false,
                    transferAgent: e.transfer_agent ? e.transfer_agent : null,
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
                    numMessagesUnread: e.message_unread ? e.message_unread : 0,
                    photo: e.photo,
                    isNew: false,
                    isMine: true,
                    answered: false,
                    transferAgent: e.transfer_agent ? e.transfer_agent : null,
                    date: e.timestamp ? new Date(e.timestamp) : null,
                    expire: e.expire ? new Date(e.expire) : null,
                    errorEx: e.error_ex ? e.error_ex : null,
                    error: e.error ? e.error : false
                });
            }
        });
        state.agtFacebookChatsList = chats;
    },
    agtFacebookReceiveNewChat (state, chat = null) {
        const from = chat && chat.from ? chat.from : null;
        const contactData = chat && chat.contact_data && chat.contact_data.nombre ? chat.contact_data.nombre : null;
        state.agtFacebookChatsList.push({
            id: chat && chat.chat_id ? chat.chat_id : null,
            from: contactData || from,
            campaignId: chat && chat.campaing_id ? chat.campaing_id : null,
            campaignName: chat && chat.campaing_name ? chat.campaing_name : '-------',
            numMessages:
                chat && chat.number_messages ? chat.number_messages : 1,
            numMessagesUnread:
                chat && chat.message_unread ? chat.message_unread : 1,
            photo: chat && chat.photo ? chat.photo : '',
            isNew: true,
            isMine: false,
            answered: false,
            transferAgent: chat && chat.transfer_agent ? chat.transfer_agent : null,
            date: chat && chat.timestamp ? new Date(chat.timestamp) : new Date(),
            expire: chat && chat.expire ? new Date(chat.expire) : null,
            errorEx: chat && chat.error_ex ? chat.error_ex : null,
            error: chat && chat.error ? chat.error : false
        });
    },
    agtFacebookSetConversationInfo (state, conversation = null) {
        state.agtFacebookConversationInfo = {
            id: conversation && conversation.id ? conversation.id : null,
            campaignId:
                conversation && conversation.campaignId
                    ? conversation.campaignId
                    : null,
            campaignName:
                conversation && conversation.campaignName
                    ? conversation.campaignName
                    : null,
            page_client_id:
                conversation && conversation.page_client_id
                    ? conversation.page_client_id
                    : null,
            client: setClientInfo(
                conversation && conversation.client ? conversation.client : null
            ),
            agent:
                conversation && conversation.agent ? conversation.agent : null,
            transferAgent:
                conversation && conversation.transferAgent
                    ? conversation.transferAgent
                    : null,
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
            messageUnreadNumber:
                conversation && conversation.messageUnreadNumber
                    ? conversation.messageUnreadNumber
                    : null,
            photo:
                conversation && conversation.photo ? conversation.photo : null,
            page: setPageInfo(
                conversation && conversation.page ? conversation.page : null
            ),
            errorEx:
                conversation && conversation.errorEx ? conversation.errorEx : null,
            error:
                conversation && conversation.error ? conversation.error : false
        };
    },
    agtFacebookRestartExpiredCoversation (state, info = null) {
        if (info) {
            state.agtFacebookConversationInfo.expire = info.expire;
            localStorage.setItem(
                'agtFacebookConversationInfo',
                JSON.stringify(state.agtFacebookConversationInfo)
            );
        }
    }
};
