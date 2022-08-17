/* eslint-disable no-unused-vars */
import OutboundRouteService from '@/services/outbound_route_service';
const service = new OutboundRouteService();

export default {
    async initOutboundRoutes ({ commit }) {
        const { status, outboundRoutes } = await service.list();
        commit('initOutboundRoutes', status === 'SUCCESS' ? outboundRoutes : []);
    },
    async initOutboundRoute ({ commit }, id = null) {
        if (id) {
            const { status, outboundRoute } = await service.detail(id);
            commit('initOutboundRoute', status === 'SUCCESS' ? outboundRoute : null);
        } else {
            commit('initOutboundRoute', null);
        }
    },
    async createOutboundRoute ({ commit }, data) {
        return await service.create(data);
    },
    async updateOutboundRoute ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async deleteOutboundRoute ({ commit }, id) {
        return await service.delete(id);
    },
    async initOutboundRouteSipTrunks ({ commit }) {
        const { status, sipTrunks } = await service.sipTrunks();
        commit('initOutboundRouteSipTrunks', status === 'SUCCESS' ? sipTrunks : []);
    },
    async initOutboundRouteOrphanTrunks ({ commit }, id) {
        const { status, orphanTrunks } = await service.orphanTrunks(id);
        commit('initOutboundRouteOrphanTrunks', status === 'SUCCESS' ? orphanTrunks : []);
    },
    async reorderOutboundRoutes ({ commit }, data) {
        return await service.reorder(data);
    },
    initDialPatternForm ({ commit }, data = null) {
        commit('initDialPatternForm', data);
    },
    initTrunkForm ({ commit }, data = null) {
        commit('initTrunkForm', data);
    },
    addTrunk ({ commit }, trunk) {
        commit('addTrunk', trunk);
    },
    removeTrunk ({ commit }, trunkId) {
        commit('removeTrunk', trunkId);
    },
    addDialPattern ({ commit }, dialPattern) {
        commit('addDialPattern', dialPattern);
    },
    removeDialPattern ({ commit }, dialPattern) {
        commit('removeDialPattern', dialPattern);
    },
    editDialPattern ({ commit }, dialPattern) {
        commit('editDialPattern', dialPattern);
    },
    editTrunk ({ commit }, trunk) {
        commit('editTrunk', trunk);
    }
};
