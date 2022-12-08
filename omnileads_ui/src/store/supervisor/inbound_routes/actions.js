/* eslint-disable no-unused-vars */
import InboundRouteService from '@/services/supervisor/inbound_route_service';
const service = new InboundRouteService();

export default {
    async initInboundRoutes ({ commit }) {
        const { status, inboundRoutes } = await service.list();
        commit('initInboundRoutes', status === 'SUCCESS' ? inboundRoutes : []);
    },
    async initInboundRouteDetail ({ commit }, id) {
        const { status, inboundRoute } = await service.detail(id);
        commit('initInboundRouteDetail', status === 'SUCCESS' ? inboundRoute : {});
    },
    initInboundRouteForm ({ commit }, data = null) {
        commit('initInboundRouteForm', data);
    },
    async initInboundRoutesDestinations ({ commit }) {
        const { status, inboundRoutesDestinations } = await service.destinations();
        commit('initInboundRoutesDestinations', status === 'SUCCESS' ? inboundRoutesDestinations : []);
    },
    async createInboundRoute ({ commit }, data) {
        return await service.create(data);
    },
    async updateInboundRoute ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async deleteInboundRoute ({ commit }, id) {
        return await service.delete(id);
    }
};
