/* eslint-disable no-unused-vars */
import Service from '@/services/supervisor/whatsapp/group_of_message_template_service';
const service = new Service();

export default {
    async initWhatsappGroupOfMessageTemplates ({ commit }) {
        const { status, data } = await service.list();
        commit('initWhatsappGroupOfMessageTemplates', status === 'SUCCESS' ? data : []);
    },
    async initWhatsappGroupOfMessageTemplate ({ commit }, { id = null, obj = null }) {
        if (obj) {
            commit('initWhatsappGroupOfMessageTemplate', obj);
            commit('initMessageTemplatesOfGroup', obj.templates.map(p => p.id));
        } else if (id) {
            const { status, data } = await service.detail(id);
            commit('initWhatsappGroupOfMessageTemplate', status === 'SUCCESS' ? data : null);
            commit('initMessageTemplatesOfGroup', data.templates.map(p => p.id));
        } else {
            commit('initWhatsappGroupOfMessageTemplate', null);
            commit('initMessageTemplatesOfGroup');
        }
    },
    async createWhatsappGroupOfMessageTemplate ({ commit }, data) {
        return await service.create(data);
    },
    async updateWhatsappGroupOfMessageTemplate ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async deleteWhatsappGroupOfMessageTemplate ({ commit }, id) {
        return await service.delete(id);
    },
    addMessageTemplateToGroup ({ commit }, data) {
        commit('addMessageTemplateToGroup', data);
    },
    removeMessageTemplateOfGroup ({ commit }, id) {
        commit('removeMessageTemplateOfGroup', id);
    }
};
