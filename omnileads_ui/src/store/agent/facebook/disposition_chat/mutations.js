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
    agtFacebookDispositionChatHistoryInit (state, history = []) {
        state.agtFacebookDispositionChatHistory = history;
    },
    agtFacebookDispositionChatOptionsInit (state, options = []) {
        state.agtFacebookDispositionChatOptions = options;
    },
    agtFacebookDispositionChatDetailInit (state, dispositionChat = null) {
        state.agtFacebookDispositionChatDetail = {
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
    agtFacebookDispositionChatSetFormFlag (state, flag = true) {
        state.agtFacebookDispositionChatFormToCreate = flag;
    }
};
