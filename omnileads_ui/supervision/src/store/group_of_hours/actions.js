/* eslint-disable no-unused-vars */
import GroupOfHourService from '@/services/group_of_hour_service';
const service = new GroupOfHourService();

export default {
    async initGroupOfHours ({ commit }) {
        const { status, groupOfHours } = await service.list();
        commit('initGroupOfHours', status === 'SUCCESS' ? groupOfHours : []);
    },
    async initGroupOfHour ({ commit }, id = null) {
        if (id) {
            const { status, groupOfHour } = await service.detail(id);
            commit('initGroupOfHour', status === 'SUCCESS' ? groupOfHour : null);
        } else {
            commit('initGroupOfHour', null);
        }
    },
    async createGroupOfHour ({ commit }, data) {
        return await service.create(data);
    },
    async updateGroupOfHour ({ commit }, { id, data }) {
        return await service.update(id, data);
    },
    async deleteGroupOfHour ({ commit }, id) {
        return await service.delete(id);
    },
    initTimeValidation ({ commit }, data = null) {
        commit('initTimeValidation', data);
    },
    addTimeValidation ({ commit }, timeValidation) {
        commit('addTimeValidation', timeValidation);
    },
    removeTimeValidation ({ commit }, timeValidation) {
        commit('removeTimeValidation', timeValidation);
    },
    editTimeValidation ({ commit }, timeValidation) {
        commit('editTimeValidation', timeValidation);
    }
};
