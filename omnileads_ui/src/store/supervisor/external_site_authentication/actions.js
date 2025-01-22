/* eslint-disable no-unused-vars */
import ExternalSiteAuthenticationService from '@/services/supervisor/external_site_authentication_service';
const service = new ExternalSiteAuthenticationService();

export default {
    async initExternalSiteAuthentications ({ commit }) {
        const { status, externalSiteAuthentications } = await service.list();
        commit('initExternalSiteAuthentications', status === 'SUCCESS' ? externalSiteAuthentications : []);
    },
    async initExternalSiteAuthentication ({ commit }, id = null) {
        if (id) {
            const { status, externalSiteAuthentication } = await service.detail(id);
            commit('initExternalSiteAuthentication', status === 'SUCCESS' ? externalSiteAuthentication : null);
        } else {
            commit('initExternalSiteAuthentication', null);
        }
    },
    async testExternalSiteAuthentication ({ commit }, data) {
        return await service.test(data);
    },
    async deleteExternalSiteAuthentication ({ commit }, id) {
        return await service.delete(id);
    },
    async createExternalSiteAuthentication ({ commit }, data) {
        return await service.create(data);
    },
    async updateExternalSiteAuthentication ({ commit }, { id, data }) {
        return await service.update(id, data);
    }
};
