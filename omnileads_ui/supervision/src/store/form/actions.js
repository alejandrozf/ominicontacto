/* eslint-disable no-unused-vars */
import FormService from '@/services/form_service';
const service = new FormService();

export default {
    async initForms ({ commit }) {
        const { forms } = await service.list();
        commit('initForms', forms);
    },
    async initFormDetail ({ commit }, id) {
        const { status, form } = await service.detail(id);
        if (status === 'SUCCESS') {
            commit('initFormDetail', form);
        } else {
            commit('initFormDetail', {});
        }
    },
    async createForm ({ commit }, data) {
        const { status } = await service.create(data);
        if (status === 'SUCCESS') {
            const { forms } = await service.list();
            commit('initForms', forms);
            return true;
        }
        return false;
    },
    async updateForm ({ commit }, { id, data }) {
        const { status } = await service.update(id, data);
        if (status === 'SUCCESS') {
            const { forms } = await service.list();
            commit('initForms', forms);
            return true;
        }
        return false;
    },
    async deleteForm ({ commit }, id) {
        const { status } = await service.delete(id);
        if (status === 'SUCCESS') {
            const { forms } = await service.list();
            commit('initForms', forms);
            return true;
        }
        return false;
    },
    async hideForm ({ commit }, id) {
        const { status } = await service.hide(id);
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
    },
    async showForm ({ commit }, id) {
        const { status } = await service.show(id);
        if (status === 'SUCCESS') {
            return true;
        }
        return false;
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
