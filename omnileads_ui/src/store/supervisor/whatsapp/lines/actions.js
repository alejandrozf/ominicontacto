/* eslint-disable no-unused-vars */
import { HTTP_STATUS } from '@/globals';
import LineService from '@/services/supervisor/whatsapp/line_service';
const service = new LineService();

export default {
    async initWhatsappLines ({ commit }) {
        const { status, data } = await service.list();
        commit('initWhatsappLines', status === HTTP_STATUS.SUCCESS ? data : []);
    },
    async initWhatsappLine ({ commit }, { id = null, line = null }) {
        if (line) {
            commit('initWhatsappLine', line);
        } else if (id) {
            const { status, data } = await service.detail(id);
            commit('initWhatsappLine', status === HTTP_STATUS.SUCCESS ? data : null);
        } else {
            commit('initWhatsappLine', null);
        }
    },
    async createWhatsappLine ({ commit }, data) {
        return await service.create(data);
    },
    async updateWhatsappLine ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async deleteWhatsappLine ({ commit }, id) {
        return await service.delete(id);
    },
    initFormFlag ({ commit }, flag = false) {
        commit('initFormFlag', flag);
    },
    async initWhatsappLineCampaigns ({ commit }) {
        try {
            const response = await service.getCampaigns();
            const { status, data } = response;
            commit('initWhatsappLineCampaigns', status === HTTP_STATUS.SUCCESS ? data : []);
            return response;
        } catch (error) {
            console.error('Error al obtener las campañas');
            console.error(error);
            commit('initWhatsappLineCampaigns', []);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener las campañas'
            };
        }
    },
    initWhatsappLineOptionForm ({ commit }, option = null) {
        commit('initWhatsappLineOptionForm', option);
    },
    createWhatsappLineOption ({ commit }, { data, menuId }) {
        commit('createWhatsappLineOption', {data, menuId});
    },
    updateWhatsappLineOption ({ commit }, { id, data, menuId }) {
        commit('updateWhatsappLineOption', { id, data, menuId});
    },
    deleteWhatsappLineOption ({ commit }, { id, menuId }) {
        console.log(2, { id, menuId } )
        commit('deleteWhatsappLineOption', { id, menuId });
    }
};
