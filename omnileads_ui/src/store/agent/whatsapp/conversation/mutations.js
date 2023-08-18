export default {
    agtWhatsCoversationSendMessage (state, message) {
        state.agtWhatsCoversationMessages.push(message);
    },
    agtWhatsCoversationReciveMessage (state, message) {
        state.agtWhatsCoversationMessages.push(message);
    },
    agtWhatsConversationInitMessages (state, message) {
        state.agtWhatsCoversationMessages = message;
    }
};
