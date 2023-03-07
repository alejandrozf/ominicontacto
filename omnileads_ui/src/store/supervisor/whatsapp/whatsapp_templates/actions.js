/* eslint-disable no-unused-vars */
import WhatsappTemplateService from '@/services/supervisor/whatsapp/whatsapp_template_service';
const service = new WhatsappTemplateService();

export default {
    async initSupWhatsappTemplates ({ commit }) {
        const { status, data } = await service.list();
        commit('initSupWhatsappTemplates', status === 'SUCCESS' ? data : []);
    },
    async sycnupWhatsappTemplates ({ commit }, lineId) {
        return await service.sycnUp(lineId);
    }
};
