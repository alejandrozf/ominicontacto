export default {
    agtWhatsTransferChatInitData (state, data) {
        state.agtWhatsTransferChatForm = {
            targetType: data?.targetType || 'agent',
            to: data?.to,
            conversationId: data?.conversationId
        };
    },
    agtWhatsTransferChatInitAgents (state, data) {
        state.agtWhatsTransferChatAgents = data;
    },
    agtWhatsTransferChatInitCampaigns (state, data) {
        state.agtWhatsTransferChatCampaigns = data;
    }
};
