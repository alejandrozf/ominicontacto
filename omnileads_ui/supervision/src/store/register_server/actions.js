/* eslint-disable no-unused-vars */
import Service from '@/services/register_server_service';
const service = new Service();

export default {
    async initRegisterServer ({ commit }) {
        const { registered, registerServer, adminName } = await service.registerInfo();
        commit('initRegisterServer', { registered, registerServer, adminName });
    },
    async createRegisterServer ({ commit }, data) {
        return await service.create(data);
    },
    async resendKeyRegisterServer ({ commit }) {
        return await service.resendKey();
    }
};
