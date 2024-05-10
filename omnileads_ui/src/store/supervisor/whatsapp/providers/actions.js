/* eslint-disable no-unused-vars */
import ProviderService from '@/services/supervisor/whatsapp/provider_service';
const service = new ProviderService();

export default {
    async initWhatsappProviders ({ commit }) {
        const { status, data } = await service.list();
        commit('initWhatsappProviders', status === 'SUCCESS' ? data : []);
    },
    async initWhatsappProvider ({ commit }, { id = null, provider = null }) {
        if (provider) {
            commit('initWhatsappProvider', provider);
        } else if (id) {
            const { status, data } = await service.detail(id);
            commit('initWhatsappProvider', status === 'SUCCESS' ? data : null);
        } else {
            commit('initWhatsappProvider', null);
        }
    },
    async createWhatsappProvider ({ commit }, data) {
        return await service.create(data);
    },
    async updateWhatsappProvider ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async deleteWhatsappProvider ({ commit }, id) {
        return await service.delete(id);
    }
};
