/* eslint-disable no-unused-vars */
import { HTTP_STATUS } from '@/globals';
import PageService from '@/services/supervisor/facebook/page_service';
const service = new PageService();

export default {
    async initFacebookPages ({ commit }) {
        const { status, data } = await service.list();
        commit('initFacebookPages', status === HTTP_STATUS.SUCCESS ? data : []);
    },
    async initFacebookPage ({ commit }, { id = null, page = null }) {
        if (page) {
            commit('initFacebookPage', page);
        } else if (id) {
            const { status, data } = await service.detail(id);
            commit('initFacebookPage', status === HTTP_STATUS.SUCCESS ? data : null);
        } else {
            commit('initFacebookPage', null);
        }
    },
    async createFacebookPage ({ commit }, data) {
        console.log('data >>>', data)
        return await service.create(data);
    },
    async updateFacebookPage ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async deleteFacebookPage ({ commit }, id) {
        return await service.delete(id);
    },
    initFormFlag ({ commit }, flag = false) {
        commit('initFormFlag', flag);
    },
    async initFacebookPageCampaigns ({ commit }) {
        try {
            const response = await service.getCampaigns();
            const { status, data } = response;
            commit('initFacebookPageCampaigns', status === HTTP_STATUS.SUCCESS ? data : []);
            return response;
        } catch (error) {
            console.error('Error al obtener las campañas');
            console.error(error);
            commit('initFacebookPageCampaigns', []);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener las campañas'
            };
        }
    },
    intFacebookPageOptionForm ({ commit }, option = null) {
        commit('initFacebookPageOptionForm', option);
    },
    createFacebookPageOption ({ commit }, { data, menuId }) {
        commit('createFacebookPageOption', {data, menuId});
    },
    updateFacebookPageOption ({ commit }, { id, data, menuId }) {
        commit('updateFacebookPageOption', { id, data, menuId});
    },
    deleteFacebookPageOption ({ commit }, { id, menuId }) {
        commit('deleteFacebookPageOption', { id, menuId });
    }
};
