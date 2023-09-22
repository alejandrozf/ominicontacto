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
    agtWhatsSetCoversationId (state, pk) {
        state.agtWhatsCoversationId = pk;
    },
    agtWhatsSetCoversationCampaignId (state, pk) {
        state.agtWhatsCoversationCampaignId = pk;
    },
    agtWhatsConversationInfoInit (state, conversation = null) {
        state.agtWhatsCoversationInfo = {
            id: conversation ? conversation.id : null,
            conversationId: conversation ? conversation.conversation_id : null,
            conversationType: conversation
                ? conversation.conversation_type
                : null,
            campaignId: conversation ? conversation.campaing_id : null,
            campaignName: conversation ? conversation.campaing_name : null,
            destination: conversation ? conversation.destination : null,
            client: conversation ? conversation.client : null,
            agent: conversation ? conversation.agent : null,
            isActive: conversation ? conversation.is_active : null,
            expire: conversation ? conversation.expire : null,
            timestamp: conversation ? conversation.timestamp : null,
            messageNumber: conversation ? conversation.message_number : null,
            photo: conversation ? conversation.photo : null,
            lineNumber: conversation ? conversation.line_number : null
        };
    },
    agtWhatsChatsListInit (state, { isNew, inProgress }) {
        const chats = [];
        isNew.forEach((e) => {
            chats.push({
                id: e.id,
                from: e.client ? e.client.name : e.destination,
                campaignId: e.campaing_id,
                campaignName: e.campaing_name,
                numMessages: e.message_number,
                photo: e.photo,
                isNew: true,
                isMine: false,
                answered: false,
                date: new Date(e.timestamp)
            });
        });
        inProgress.forEach((e) => {
            chats.push({
                id: e.id,
                from: e.client ? e.client.name : e.destination,
                campaignId: e.campaing_id,
                campaignName: e.campaing_name,
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
                campaignId: chat.campaing_id,
                campaignName: chat.campaing_name,
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
