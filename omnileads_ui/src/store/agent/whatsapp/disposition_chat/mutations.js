export default {
    agtWhatsDispositionChatHistoryInit (state, history) {
        state.agtWhatsDispositionChatHistory = history;
    },
    agtWhatsDispositionChatOptionsInit (state, options) {
        state.agtWhatsDispositionChatOptions = options;
    },
    agtWhatsDispositionChatDetailInit (state, dispositionChat = null) {
        state.agtWhatsDispositionChatDetail = {
            id: dispositionChat ? dispositionChat.id : null,
            contact: {
                id: dispositionChat ? dispositionChat.contact.id : null,
                phone: dispositionChat ? dispositionChat.contact.phone : null,
                data: dispositionChat ? dispositionChat.contact.data : null
            },
            agent: {
                id: dispositionChat ? dispositionChat.agent.id : null,
                name: dispositionChat ? dispositionChat.agent.name : null,
                email: dispositionChat ? dispositionChat.agent.email : null
            },
            comments: dispositionChat ? dispositionChat.comments : null,
            form_response: dispositionChat ? dispositionChat.form_response : null,
            disposition_data: dispositionChat ? dispositionChat.disposition_data : null
        };
    },
    agtWhatsDispositionChatSetFormFlag (state, flag) {
        state.agtWhatsDispositionChatFormToCreate = flag;
    }
};
