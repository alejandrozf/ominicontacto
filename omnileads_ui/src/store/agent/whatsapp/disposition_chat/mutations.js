/* eslint-disable */
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
                id: dispositionChat.contact
                    ? dispositionChat.contact.id || null
                    : null,
                phone: dispositionChat.contact
                    ? dispositionChat.contact.phone || null
                    : null,
                data: dispositionChat.contact
                    ? dispositionChat.contact.data || null
                    : null
            },
            agent: {
                id: dispositionChat.agent ? dispositionChat.agent.id || null : null,
                name: dispositionChat.agent
                    ? dispositionChat.agent.name || null
                    : null,
                email: dispositionChat.agent
                    ? dispositionChat.agent.email || null
                    : null
            },
            comments: dispositionChat ? dispositionChat.comments : null,
            form_response: dispositionChat
                ? dispositionChat.form_response
                : null,
            disposition_data: dispositionChat
                ? dispositionChat.disposition_data
                : null
        };
    },
    agtWhatsDispositionChatSetFormFlag (state, flag) {
        state.agtWhatsDispositionChatFormToCreate = flag;
    }
};
