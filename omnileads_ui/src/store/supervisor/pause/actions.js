/* eslint-disable no-unused-vars */
import PauseService from '@/services/supervisor/pause_service';
const service = new PauseService();

export default {
    async initPauses ({ commit }) {
        const { status, pauses } = await service.list();
        commit('initPauses', status === 'SUCCESS' ? pauses : []);
    },
    async initPauseDetail ({ commit }, id) {
        const { status, pause } = await service.detail(id);
        commit('initPauseDetail', status === 'SUCCESS' ? pause : {});
    },
    initPauseForm ({ commit }, data = null) {
        commit('initPauseForm', data);
    },
    async createPause ({ commit }, data) {
        return await service.create(data);
    },
    async updatePause ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async deletePause ({ commit }, id) {
        return await service.delete(id);
    },
    async reactivatePause ({ commit }, id) {
        return await service.reactivate(id);
    }
};
