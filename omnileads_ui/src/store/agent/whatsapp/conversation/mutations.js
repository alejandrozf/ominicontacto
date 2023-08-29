export default {
    agtWhatsCoversationSendMessage (state, message) {
        state.agtWhatsCoversationMessages.push(message);
    },
    agtWhatsCoversationReciveMessage (state, message) {
        state.agtWhatsCoversationMessages.push(message);
    },
    agtWhatsConversationInitMessages (state, message) {
        state.agtWhatsCoversationMessages = message;
    },
    agtWhatsChatsListInit (state, { isNew, inProgress }) {
        const chats = [];
        isNew.forEach(e => {
            chats.push({
                id: e.id,
                from: e.client_name,
                campaing_id: e.campaing_id,
                campaing_name: e.campaing_name,
                numMessages: e.number_messages,
                photo: e.photo,
                isNew: true,
                isMine: false,
                answered: false,
                date: new Date(e.date)
            });
        });
        inProgress.forEach(e => {
            chats.push({
                id: e.id,
                from: e.client_name,
                campaing_id: e.campaing_id,
                campaing_name: e.campaing_name,
                numMessages: e.number_messages,
                photo: e.photo,
                isNew: false,
                isMine: true,
                answered: false,
                date: new Date(e.date)
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
