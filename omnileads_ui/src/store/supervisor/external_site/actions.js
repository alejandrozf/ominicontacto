/* eslint-disable no-unused-vars */
import ExternalSiteService from '@/services/supervisor/external_site_service';
const service = new ExternalSiteService();

export default {
    async initExternalSites ({ commit }) {
        const { externalSites } = await service.list();
        commit('initExternalSites', externalSites);
    },
    async initExternalSitesDynamicList ({ commit }) {
        const { externalSites } = await service.list();
        commit('initExternalSitesDynamicList', externalSites);
    },
    async initExternalSiteDetail ({ commit }, id) {
        const { externalSiteDetail } = await service.detail(id);
        commit('initExternalSiteDetail', externalSiteDetail);
    },
    async deleteExternalSite ({ commit }, id) {
        return await service.delete(id);
    },
    async hideExternalSite ({ commit }, id) {
        return await service.hide(id);
    },
    async showExternalSite ({ commit }, id) {
        return await service.show(id);
    },
    async createExternalSite ({ commit }, data) {
        const response = await service.create(data);
        const { status } = response;
        if (status === 'SUCCESS') {
            const { externalSites } = await service.list();
            commit('initExternalSites', externalSites);
        }
        return response;
    },
    async updateExternalSite ({ commit }, { id, data }) {
        const response = await service.update(id, data);
        const { status } = response;
        if (status === 'SUCCESS') {
            const { externalSites } = await service.list();
            commit('initExternalSites', externalSites);
        }
        return response;
    }
};
