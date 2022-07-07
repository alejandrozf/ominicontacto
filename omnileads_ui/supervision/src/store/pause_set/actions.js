/* eslint-disable no-unused-vars */
import PauseSetService from '@/services/pause_set_service.js';
const service = new PauseSetService();

export default {
    async initPauseSets ({ commit }) {
        const { pauseSets } = await service.getPauseSetsList();
        commit('initPauseSets', pauseSets);
    },
    async initPauseSetDetail ({ commit }, idPauseGroup) {
        const { pauseSetDetail } = await service.getPauseSetDetail(idPauseGroup);
        commit('initPauseSetDetail', pauseSetDetail);
    },
    async deletePauseSet ({ commit }, id) {
        const { status } = await service.deletePauseSet(id);
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async initPauses ({ commit }) {
        const { pauses } = await service.getPauses();
        commit('initPauses', pauses);
    },
    async createPauseSet ({ commit }, pauseGroupData) {
        const { status } = await service.createPauseSet(pauseGroupData);
        if (status === 'SUCCESS') {
            const { pauseSets } = await service.getPauseSetsList();
            commit('initPauseSets', pauseSets);
            return true;
        }
        return false;
    },
    async updatePauseSetName ({ commit }, { id, name }) {
        const { status } = await service.updatePauseSetName(id, { nombre: name });
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
