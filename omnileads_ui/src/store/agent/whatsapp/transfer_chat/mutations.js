export default {
    agtWhatsTransferChatInitData (state, data) {
        state.agtWhatsTransferChatForm = {
            from: data?.from,
            to: data?.to,
            conversationId: data?.conversationId
        };
    },
    agtWhatsTransferChatInitAgents (state, data) {
        state.agtWhatsTransferChatAgents = data;
    }
};
