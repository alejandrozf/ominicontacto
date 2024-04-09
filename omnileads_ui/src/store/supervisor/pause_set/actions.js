/* eslint-disable no-unused-vars */
import PauseSetService from '@/services/supervisor/pause_set_service.js';
const service = new PauseSetService();

export default {
    async initPauseSets ({ commit }) {
        const { pauseSets } = await service.list();
        commit('initPauseSets', pauseSets);
    },
    async initPauseSetDetail ({ commit }, id) {
        const { pauseSetDetail } = await service.detail(id);
        commit('initPauseSetDetail', pauseSetDetail);
    },
    async deletePauseSet ({ commit }, id) {
        const { status } = await service.delete(id);
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async initActivePauses ({ commit }) {
        const { pauses } = await service.getPauses();
        commit('initActivePauses', pauses);
    },
    async createPauseSet ({ commit }, data) {
        const { status } = await service.create(data);
        if (status === 'SUCCESS') {
            const { pauseSets } = await service.list();
            commit('initPauseSets', pauseSets);
            return true;
        }
        return false;
    },
    async updatePauseSetName ({ commit }, { id, name }) {
        const { status } = await service.update(id, { nombre: name });
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async deletePauseConfig ({ commit }, id) {
        const { status } = await service.deletePauseConfig(id);
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async updatePauseConfig ({ commit }, { id, timeToEndPause }) {
        const { status } = await service.updatePauseConfig(id, { timeToEndPause });
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async createPauseConfig ({ commit }, { pauseId, setId, timeToEndPause }) {
        const { status } = await service.createPauseConfig({ pauseId, setId, timeToEndPause });
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    }
};
