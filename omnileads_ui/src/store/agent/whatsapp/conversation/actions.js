/* eslint-disable no-unused-vars */
import Service from '@/services/agent/whatsapp/conversation_service';
const service = new Service();

export default {
    agtWhatsCoversationSendMessage ({ commit }, message) {
        commit('agtWhatsCoversationSendMessage', message);
    },
    agtWhatsConversationInitMessages ({ commit }, id) {
        const messages = service.getMessagesByConversationId(id);
        commit('agtWhatsConversationInitMessages', messages);
    }
};
