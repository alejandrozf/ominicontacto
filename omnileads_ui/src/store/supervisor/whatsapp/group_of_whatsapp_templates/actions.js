/* eslint-disable no-unused-vars */
import Service from '@/services/supervisor/whatsapp/group_of_whatsapp_template_service';
const service = new Service();

export default {
    async initWhatsappGroupOfWhatsappTemplates ({ commit }) {
        const { status, data } = await service.list();
        commit('initWhatsappGroupOfWhatsappTemplates', status === 'SUCCESS' ? data : []);
    },
    async initWhatsappGroupOfWhatsappTemplate ({ commit }, { id = null, obj = null }) {
        if (obj) {
            commit('initWhatsappGroupOfWhatsappTemplate', obj);
            commit('initWhatsappTemplatesOfGroup', obj.templates.map(p => p.id));
        } else if (id) {
            const { status, data } = await service.detail(id);
            commit('initWhatsappGroupOfWhatsappTemplate', status === 'SUCCESS' ? data : null);
            commit('initWhatsappTemplatesOfGroup', data.templates.map(p => p.id));
        } else {
            commit('initWhatsappGroupOfWhatsappTemplate', null);
            commit('initWhatsappTemplatesOfGroup');
        }
    },
    async createWhatsappGroupOfWhatsappTemplate ({ commit }, data) {
        return await service.create(data);
    },
    async updateWhatsappGroupOfWhatsappTemplate ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async deleteWhatsappGroupOfWhatsappTemplate ({ commit }, id) {
        return await service.delete(id);
    },
    addWhatsappTemplateToGroup ({ commit }, data) {
        commit('addWhatsappTemplateToGroup', data);
    },
    removeWhatsappTemplateOfGroup ({ commit }, id) {
        commit('removeWhatsappTemplateOfGroup', id);
    }
};
