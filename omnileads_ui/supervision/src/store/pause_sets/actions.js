import PauseSetService from '@/services/pauseSetService.js';
const pauseSetService = new PauseSetService();

export default {
    async initPauseSets ({ commit }) {
        const { pauseSets } = await pauseSetService.getPauseSetsList();
        commit('initPauseSets', pauseSets);
    },
    async initPauseSetDetail ({ commit }, idPauseGroup) {
        const { pauseSetDetail } = await pauseSetService.getPauseSetDetail(idPauseGroup);
        commit('initPauseSetDetail', pauseSetDetail);
    },
    async deletePauseSet (id) {
        const { status } = await pauseSetService.deletePauseSet(id);
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async initPauses ({ commit }) {
        const { pauses } = await pauseSetService.getPauses();
        commit('initPauses', pauses);
    },
    async createPauseSet ({ commit }, pauseGroupData) {
        const { status } = await pauseSetService.createPauseSet(pauseGroupData);
        if (status === 'SUCCESS') {
            const { pauseSets } = await pauseSetService.getPauseSetsList();
            commit('initPauseSets', pauseSets);
            return true;
        }
        return false;
    },
    async updatePauseSetName ({ id, name }) {
        const { status } = await pauseSetService.updatePauseSetName(id, { nombre: name });
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async deletePauseConfig (id) {
        const { status } = await pauseSetService.deletePauseConfig(id);
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async updatePauseConfig ({ id, timeToEndPause }) {
        const { status } = await pauseSetService.updatePauseConfig(id, { timeToEndPause });
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async createPauseConfig ({ pauseId, setId, timeToEndPause }) {
        const { status } = await pauseSetService.createPauseConfig({ pauseId, setId, timeToEndPause });
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    }
};
