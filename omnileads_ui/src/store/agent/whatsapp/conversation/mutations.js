export default {
    agtWhatsCoversationSendMessage (state, message) {
        state.agtWhatsCoversationMessages.push(message);
    },
    agtWhatsCoversationReciveMessage (state, message) {
        state.agtWhatsCoversationMessages.push(message);
    },
    agtWhatsConversationInitMessages (state, messages) {
        state.agtWhatsCoversationMessages = messages;
    },
    agtWhatsConversationInfoInit (state, conversation) {
        state.agtWhatsCoversationInfo = {
            id: conversation.id,
            conversationId: conversation.conversation_id,
            conversationType: conversation.conversation_type,
            campaingId: conversation.campaing_id,
            campaingName: conversation.campaing_name,
            destination: conversation.destination,
            client: conversation.client,
            agent: conversation.agent,
            isActive: conversation.is_active,
            expire: conversation.expire,
            timestamp: conversation.timestamp,
            messageNumber: conversation.message_number,
            photo: conversation.photo,
            lineNumber: conversation.line_number
        };
    },
    agtWhatsChatsListInit (state, { isNew, inProgress }) {
        const chats = [];
        isNew.forEach(e => {
            chats.push({
                id: e.id,
                from: e.client ? e.client.name : e.destination,
                campaing_id: e.campaing_id,
                campaing_name: e.campaing_name,
                numMessages: e.message_number,
                photo: e.photo,
                isNew: true,
                isMine: false,
                answered: false,
                date: new Date(e.timestamp)
            });
        });
        inProgress.forEach(e => {
            chats.push({
                id: e.id,
                from: e.client ? e.client.name : e.destination,
                campaing_id: e.campaing_id,
                campaing_name: e.campaing_name,
                numMessages: e.message_number,
                photo: e.photo,
                isNew: false,
                isMine: true,
                answered: false,
                date: new Date(e.timestamp)
            });
        });
        state.agtWhatsChatsList = chats;
    },
    agtWhatsReceiveNewChat (state, chat = null) {
        if (chat) {
            state.agtWhatsChatsList.push({
                id: chat.id,
                from: chat.client_name,
                campaing_id: chat.campaing_id,
                campaing_name: chat.campaing_name,
                numMessages: chat.number_messages,
                photo: chat.photo,
                isNew: true,
                isMine: false,
                answered: false,
                date: new Date(chat.date)
            });
        }
    }
};
