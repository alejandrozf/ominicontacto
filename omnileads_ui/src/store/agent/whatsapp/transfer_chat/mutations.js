export default {
    agtWhatsTransferChatInitData (state, data) {
        state.agtWhatsTransferChatForm = {
            to: data?.to,
            conversationId: data?.conversationId
        };
    },
    agtWhatsTransferChatInitAgents (state, data) {
        state.agtWhatsTransferChatAgents = data;
    }
};
