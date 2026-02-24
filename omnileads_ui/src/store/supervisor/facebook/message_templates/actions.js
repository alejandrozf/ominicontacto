/* eslint-disable no-unused-vars */
import MessageTemplateService from '@/services/supervisor/facebook/message_template_service';
const service = new MessageTemplateService();

export default {
    async initFacebookPageTemplates ({ commit }) {
        console.log('initFacebookPageTemplates111 >>>') 
        const { status, data } = await service.list();
        console.log('initFacebookPageTemplates data >>>', data)
        commit('initFacebookPageTemplates', status === 'SUCCESS' ? data : []);
    },
    async initFacebookPageTemplate ({ commit }, { id = null, messageTemplate = null }) {
        if (messageTemplate) {
            commit('initFacebookPageTemplate', messageTemplate);
        } else if (id) {
            const { status, data } = await service.detail(id);
            commit('initFacebookPageTemplate', status === 'SUCCESS' ? data : null);
        } else {
            commit('initFacebookPageTemplate', null);
        }
    },
    initFacebookPageTemplateFormFields ({ commit }, { type = null, config = null }) {
        commit('initFacebookPageTemplateFormFields', { type, config });
    },
    async createFacebookPageTemplate ({ commit }, data) {
        return await service.create(data);
    },
    async updateFacebookPageTemplate ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async deleteFacebookPageTemplate ({ commit }, id) {
        return await service.delete(id);
    }
};
