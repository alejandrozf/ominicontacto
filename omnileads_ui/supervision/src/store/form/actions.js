/* eslint-disable no-unused-vars */
import FormService from '@/services/form_service';
const service = new FormService();

export default {
    async initForms ({ commit }) {
        const { status, forms } = await service.list();
        commit('initForms', status === 'SUCCESS' ? forms : []);
    },
    async initFormDetail ({ commit }, id) {
        const { status, form } = await service.detail(id);
        commit('initFormDetail', status === 'SUCCESS' ? form : {});
    },
    async createForm ({ commit }, data) {
        const response = await service.create(data);
        const { status } = response;
        if (status === 'SUCCESS') {
            const { status, forms } = await service.list();
            commit('initForms', status === 'SUCCESS' ? forms : []);
        }
        return response;
    },
    async updateForm ({ commit }, { id, data }) {
        const response = await service.update(id, data);
        const { status } = response;
        if (status === 'SUCCESS') {
            const { status, forms } = await service.list();
            commit('initForms', status === 'SUCCESS' ? forms : []);
        }
        return response;
    },
    async deleteForm ({ commit }, id) {
        const response = await service.delete(id);
        const { status } = response;
        if (status === 'SUCCESS') {
            const { status, forms } = await service.list();
            commit('initForms', status === 'SUCCESS' ? forms : []);
        }
        return response;
    },
    async hideForm ({ commit }, id) {
        return await service.hide(id);
    },
    async showForm ({ commit }, id) {
        return await service.show(id);
    },
    initNewForm ({ commit }, data = null) {
        commit('initNewForm', data);
    },
    initNewFormField ({ commit }, data = null) {
        commit('initNewFormField', data);
    },
    initOptionListValues ({ commit }) {
        commit('initOptionListValues');
    },
    addValueOption ({ commit }, valueOption) {
        commit('addValueOption', valueOption);
    },
    removeValueOption ({ commit }, id) {
        commit('removeValueOption', id);
    },
    addFormField ({ commit }, formField) {
        commit('addFormField', formField);
    },
    removeFormField ({ commit }, formField) {
        commit('removeFormField', formField);
    },
    initFormToCreateFlag ({ commit }, flag) {
        commit('initFormToCreateFlag', flag);
    }
};
