/* eslint-disable no-unused-vars */
import Service from '@/services/supervisor/facebook/group_of_message_template_service';
const service = new Service();

export default {
    async initFacebookPageGroupOfMessageTemplates ({ commit }) {
        const { status, data } = await service.list();
        commit('initFacebookPageGroupOfMessageTemplates', status === 'SUCCESS' ? data : []);
    },
    async initFacebookPageGroupOfMessageTemplate ({ commit }, { id = null, obj = null }) {
        if (obj) {
            commit('initFacebookPageGroupOfMessageTemplate', obj);
            commit('initMessageTemplatesOfGroup', obj.templates.map(p => p.id));
        } else if (id) {
            const { status, data } = await service.detail(id);
            commit('initFacebookPageGroupOfMessageTemplate', status === 'SUCCESS' ? data : null);
            commit('initMessageTemplatesOfGroup', data.templates.map(p => p.id));
        } else {
            commit('initFacebookPageGroupOfMessageTemplate', null);
            commit('initMessageTemplatesOfGroup');
        }
    },
    async createFacebookPageGroupOfMessageTemplate ({ commit }, data) {
        return await service.create(data);
    },
    async updateFacebookPageGroupOfMessageTemplate ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async deleteFacebookPageGroupOfMessageTemplate ({ commit }, id) {
        return await service.delete(id);
    },
    addMessageTemplateToGroup ({ commit }, data) {
        commit('addMessageTemplateToGroup', data);
    },
    removeMessageTemplateOfGroup ({ commit }, id) {
        commit('removeMessageTemplateOfGroup', id);
    }
};
