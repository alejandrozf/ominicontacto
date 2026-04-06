export default {
    agtFacebookTransferChatInitData (state, data) {
        state.agtFacebookTransferChatForm = {
            to: data?.to,
            conversationId: data?.conversationId
        };
    },
    agtFacebookTransferChatInitAgents (state, data) {
        state.agtFacebookTransferChatAgents = data;
    }
};
