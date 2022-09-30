/* eslint-disable no-unused-vars */
import ExternalSystemService from '@/services/external_system_service';
const service = new ExternalSystemService();

export default {
    async initAgentsExternalSystems ({ commit }) {
        const { status, agents } = await service.getAgents();
        commit('initAgentsExternalSystems', status === 'SUCCESS' ? agents : []);
    },
    async initExternalSystems ({ commit }) {
        const { status, externalSystems } = await service.list();
        commit('initExternalSystems', status === 'SUCCESS' ? externalSystems : []);
    },
    async initExternalSystemDetail ({ commit }, id) {
        const { status, externalSystem } = await service.detail(id);
        commit('initExternalSystemDetail', status === 'SUCCESS' ? externalSystem : {});
    },
    async createExternalSystem ({ commit }, data) {
        const response = await service.create(data);
        const { status } = response;
        if (status === 'SUCCESS') {
            const { status, externalSystems } = await service.list();
            commit('initExternalSystems', status === 'SUCCESS' ? externalSystems : []);
        }
        return response;
    },
    async updateExternalSystem ({ commit }, { id, data }) {
        const response = await service.update(id, data);
        const { status } = response;
        if (status === 'SUCCESS') {
            const { status, externalSystems } = await service.list();
            commit('initExternalSystems', status === 'SUCCESS' ? externalSystems : []);
        }
        return response;
    }
};
