/* eslint-disable no-unused-vars */
import ExternalSystemService from '@/services/external_system_service';
const service = new ExternalSystemService();

export default {
    async initAgentsExternalSystems ({ commit }) {
        const { agents } = await service.getAgents();
        commit('initAgentsExternalSystems', agents);
    },
    async initExternalSystems ({ commit }) {
        const { externalSystems } = await service.list();
        commit('initExternalSystems', externalSystems);
    },
    async initExternalSystemDetail ({ commit }, id) {
        const { status, externalSystem } = await service.detail(id);
        if (status === 'SUCCESS') {
            commit('initExternalSystemDetail', externalSystem);
        } else {
            commit('initExternalSystemDetail', {});
        }
    },
    async createExternalSystem ({ commit }, data) {
        const { status } = await service.create(data);
        if (status === 'SUCCESS') {
            const { externalSystems } = await service.list();
            commit('initExternalSystems', externalSystems);
            return true;
        }
        return false;
    },
    async updateExternalSystem ({ commit }, { id, data }) {
        const { status } = await service.update(id, data);
        if (status === 'SUCCESS') {
            const { externalSystems } = await service.list();
            commit('initExternalSystems', externalSystems);
            return true;
        }
        return false;
    }
};
