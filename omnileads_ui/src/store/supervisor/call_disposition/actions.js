/* eslint-disable no-unused-vars */
import CallDispositionService from '@/services/supervisor/call_disposition_service';
const service = new CallDispositionService();

export default {
    async initCallDispositions ({ commit }) {
        const { callDispositions } = await service.list();
        commit('initCallDispositions', callDispositions);
    },
    async deleteCallDisposition ({ commit }, id) {
        const { status } = await service.delete(id);
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async createCallDisposition ({ commit }, data) {
        const { status } = await service.create(data);
        if (status === 'SUCCESS') {
            const { callDispositions } = await service.list();
            commit('initCallDispositions', callDispositions);
            return true;
        }
        return false;
    },
    async updateCallDisposition ({ commit }, { id, data }) {
        const { status } = await service.update(id, data);
        if (status === 'SUCCESS') {
            const { callDispositions } = await service.list();
            commit('initCallDispositions', callDispositions);
            return true;
        }
        return false;
    }
};
