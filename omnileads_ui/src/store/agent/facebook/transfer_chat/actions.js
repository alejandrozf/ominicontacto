/* eslint-disable no-unused-vars */
import FacebookTransferChatService from '@/services/agent/facebook/transfer_service';
import { HTTP_STATUS } from '@/globals';
const transferService = new FacebookTransferChatService();

export default {
    async agtFacebookTransferChatInitData ({ commit }, { campaingId = null }) {
        try {
            if (!campaingId) {
                await commit('agtFacebookTransferChatInitAgents', []);
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener Agentes'
                };
            }
            const response = await transferService.getActiveAgents({
                campaingId
            });
            const { status, data } = response;
            await commit(
                'agtFacebookTransferChatInitAgents',
                status === HTTP_STATUS.SUCCESS ? data : []
            );
            return response;
        } catch (error) {
            console.error('agtFacebookTransferChatInitData');
            console.error(error);
            await commit('agtFacebookTransferChatInitAgents', []);
        }
    },
    async agtFacebookTransferChatSend ({ commit }, postData) {
        const { status } = await transferService.transferToagent(postData);
        if (status === HTTP_STATUS.SUCCESS) {
            return {
                status: HTTP_STATUS.SUCCESS,
                message: 'Se transfirio satisfactoriamente el chat'
            };
        } else {
            return {
                status: HTTP_STATUS.ERROR,
                message: 'No se pudo transferir el chat'
            };
        }
    }
};
