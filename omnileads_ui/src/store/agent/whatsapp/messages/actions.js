/* eslint-disable no-unused-vars */
export default {
    agtWhatSendMessageStatus ({ commit }, info = null) {
        try {
            commit('agtWhatSendMessageStatus', info);
        } catch (error) {
            console.error('===> ERROR al actualizar el status del mensaje');
            console.error(error);
            commit('agtWhatSendMessageStatus', null);
        }
    }
};
