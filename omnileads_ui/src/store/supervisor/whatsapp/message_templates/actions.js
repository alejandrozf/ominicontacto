/* eslint-disable no-unused-vars */
import MessageTemplateService from '@/services/supervisor/whatsapp/message_template_service';
const service = new MessageTemplateService();

export default {
    async initWhatsappMessageTemplates ({ commit }) {
        const { status, data } = await service.list();
        commit('initWhatsappMessageTemplates', status === 'SUCCESS' ? data : []);
    },
    async initWhatsappMessageTemplate ({ commit }, { id = null, messageTemplate = null }) {
        if (messageTemplate) {
            commit('initWhatsappMessageTemplate', messageTemplate);
        } else if (id) {
            const { status, data } = await service.detail(id);
            commit('initWhatsappMessageTemplate', status === 'SUCCESS' ? data : null);
        } else {
            commit('initWhatsappMessageTemplate', null);
        }
    },
    initWhatsappMessageTemplateFormFields ({ commit }, { type = null, config = null }) {
        commit('initWhatsappMessageTemplateFormFields', { type, config });
    },
    async createWhatsappMessageTemplate ({ commit }, data) {
        return await service.create(data);
    },
    async updateWhatsappMessageTemplate ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async deleteWhatsappMessageTemplate ({ commit }, id) {
        return await service.delete(id);
    }
};
