/* eslint-disable no-unused-vars */
export default {
    agtFacebookSendMessageStatus ({ commit }, info = null) {
        try {
            commit('agtFacebookSendMessageStatus', info);
        } catch (error) {
            console.error('===> ERROR al actualizar el status del mensaje');
            console.error(error);
            commit('agtFacebookSendMessageStatus', null);
        }
    }
};
