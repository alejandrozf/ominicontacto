/* eslint-disable no-unused-vars */
import ExternalSiteService from '@/services/external_site_service';
const service = new ExternalSiteService();

export default {
    async initExternalSites ({ commit }) {
        const { externalSites } = await service.list();
        commit('initExternalSites', externalSites);
    },
    async initExternalSiteDetail ({ commit }, id) {
        const { externalSiteDetail } = await service.detail(id);
        commit('initExternalSiteDetail', externalSiteDetail);
    },
    async deleteExternalSite ({ commit }, id) {
        const { status } = await service.delete(id);
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async hideExternalSite ({ commit }, id) {
        const { status } = await service.hide(id);
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async showExternalSite ({ commit }, id) {
        const { status } = await service.show(id);
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async createExternalSite ({ commit }, data) {
        const { status } = await service.create(data);
        if (status === 'SUCCESS') {
            const { externalSites } = await service.list();
            commit('initExternalSites', externalSites);
            return true;
        }
        return false;
    },
    async updateExternalSite ({ commit }, { id, data }) {
        const { status } = await service.update(id, data);
        if (status === 'SUCCESS') {
            const { externalSites } = await service.list();
            commit('initExternalSites', externalSites);
            return true;
        }
        return false;
    }
};
