/* eslint-disable no-unused-vars */
import WhatsappTemplateService from '@/services/supervisor/whatsapp/whatsapp_template_service';
const service = new WhatsappTemplateService();

export default {
    async initSupWhatsappTemplates ({ commit }) {
        const { status, data } = await service.list();
        commit('initSupWhatsappTemplates', status === 'SUCCESS' ? data : []);
    },
    async initSupWhatsappTemplate ({ commit }, { id = null, template = null }) {
        if (template) {
            commit('initSupWhatsappTemplate', template);
        } else if (id) {
            const { status, data } = await service.detail(id);
            commit('initSupWhatsappTemplate', status === 'SUCCESS' ? data : null);
        } else {
            commit('initSupWhatsappTemplate', null);
        }
    },
    async sycnupWhatsappTemplates ({ commit }, lineId) {
        return await service.sycnUp(lineId);
    }
};
