export default {
    agentList: (campaingId) => `/api/v1/whatsapp/transfer/${campaingId}/agents`,
    transferToagent: () => `/api/v1/whatsapp/transfer/to_agent`
};
