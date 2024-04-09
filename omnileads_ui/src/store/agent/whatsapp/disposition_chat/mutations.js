/* eslint-disable */
const getContactData = (contact =  null) => {
    return {
        id: contact && contact.id ? contact.id : null,
        phone: contact && contact.phone ? contact.phone : null,
        data: contact && contact.data ? contact.data : null,
        disposition: contact && contact.disposition ? contact.disposition : null
    };
};

const getAgentData = (agent = null) => {
    return {
        id: agent && agent.id ? agent.id : null,
        name: agent && agent.name ? agent.name : null,
        email: agent && agent.email ? agent.email : null
    };
};

export default {
    agtWhatsDispositionChatHistoryInit (state, history = []) {
        state.agtWhatsDispositionChatHistory = history;
    },
    agtWhatsDispositionChatOptionsInit (state, options = []) {
        state.agtWhatsDispositionChatOptions = options;
    },
    agtWhatsDispositionChatDetailInit (state, dispositionChat = null) {
        state.agtWhatsDispositionChatDetail = {
            id: dispositionChat && dispositionChat.id ? dispositionChat.id : null,
            contact: getContactData(dispositionChat && dispositionChat.contact ? dispositionChat.contact : null),
            agent: getAgentData(dispositionChat && dispositionChat.agent ? dispositionChat.agent : null),
            comments: dispositionChat && dispositionChat.comments ? dispositionChat.comments : null,
            form_response: dispositionChat && dispositionChat.form_response
                ? dispositionChat.form_response
                : null,
            disposition_data: dispositionChat && dispositionChat.disposition_data
                ? dispositionChat.disposition_data
                : null
        };
    },
    agtWhatsDispositionChatSetFormFlag (state, flag = true) {
        state.agtWhatsDispositionChatFormToCreate = flag;
    }
};
