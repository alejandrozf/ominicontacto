/* eslint-disable no-unused-vars */
import IVRService from '@/services/supervisor/ivr_service';
import { getNewFormData } from '@/helpers/ivr_helper';
import {
    MAIN_AUDIO,
    TIME_OUT_AUDIO,
    INVALID_AUDIO,
    TIME_OUT_DEST,
    INVALID_DEST
} from '@/globals/supervisor/ivr';
const service = new IVRService();

export default {
    async initIVRs ({ commit }) {
        const { status, data } = await service.list();
        commit('initIVRs', status === 'SUCCESS' ? data : []);
    },
    async initIVR ({ commit }, id = null) {
        if (id) {
            const { status, data } = await service.detail(id);
            commit('initIVR', status === 'SUCCESS' ? data : null);
        } else {
            commit('initIVR', null);
        }
    },
    async createIVR ({ commit }, data) {
        const newData = await getNewFormData(data);
        return await service.create(newData);
    },
    async updateIVR ({ commit }, { id, data }) {
        const newData = await getNewFormData(data);
        return await service.update(id, newData);
    },
    async deleteIVR ({ commit }, id) {
        return await service.delete(id);
    },
    async initIVRAudios ({ commit }) {
        const { status, data } = await service.ivrAudios();
        commit('initIVRAudios', status === 'SUCCESS' ? data : []);
    },
    async initIVRDestinations ({ commit }) {
        const { status, data } = await service.ivrDestinations();
        commit('initIVRDestinations', status === 'SUCCESS' ? data : []);
    },
    initDestinationOption ({ commit }, data = null) {
        commit('initDestinationOption', data);
    },
    addDestinationOption ({ commit }, destinationOption) {
        commit('addDestinationOption', destinationOption);
    },
    removeDestinationOption ({ commit }, destinationOption) {
        commit('removeDestinationOption', destinationOption);
    },
    editDestinationOption ({ commit }, destinationOption) {
        commit('editDestinationOption', destinationOption);
    },
    updateDestination ({ commit }, { data, option }) {
        if (option === TIME_OUT_DEST) {
            commit('updateTimeOutDestination', data);
        } else if (option === INVALID_DEST) {
            commit('updateInvalidDestination', data);
        }
    },
    setAudio ({ commit }, { data, option }) {
        if (option === MAIN_AUDIO) {
            commit('setMainAudio', data);
        } else if (option === TIME_OUT_AUDIO) {
            commit('setTimeOutAudio', data);
        } else if (option === INVALID_AUDIO) {
            commit('setInvalidAudio', data);
        }
    }
};
