/* eslint-disable no-unused-vars */
import WhatsappTransferChatService from '@/services/agent/whatsapp/transfer_service';
import { HTTP_STATUS } from '@/globals';
const transferService = new WhatsappTransferChatService();

export default {
    async agtWhatsTransferChatInitData ({ commit }, { campaingId = null }) {
        try {
            if (!campaingId) {
                await commit('agtWhatsTransferChatInitAgents', []);
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
                'agtWhatsTransferChatInitAgents',
                status === HTTP_STATUS.SUCCESS ? data : []
            );
            return response;
        } catch (error) {
            console.error('agtWhatsTransferChatInitData');
            console.error(error);
            await commit('agtWhatsTransferChatInitAgents', []);
        }
    },
    async agtWhatsTransferChatSend ({ commit }, postData) {
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
