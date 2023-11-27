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
        const { status, data } = await service.getCampaigns();
        commit('initWhatsappLineCampaigns', status === HTTP_STATUS.SUCCESS ? data : []);
    },
    initWhatsappLineOptionForm ({ commit }, option = null) {
        commit('initWhatsappLineOptionForm', option);
    },
    createWhatsappLineOption ({ commit }, { data }) {
        commit('createWhatsappLineOption', data);
    },
    updateWhatsappLineOption ({ commit }, { id, data }) {
        commit('updateWhatsappLineOption', { id, data });
    },
    deleteWhatsappLineOption ({ commit }, { id }) {
        commit('deleteWhatsappLineOption', id);
    }
};
