export default {
    agtWhatSendMessageStatus (state, info = null) {
        if (info) {
            state.agtWhatsCoversationMessages.forEach((message) => {
                if (message.id === info.message_id) { message.status = info.status; }
            });
        }
    }
};
