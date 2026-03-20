/* eslint-disable no-unused-vars */
import WhatsappTransferChatService from '@/services/agent/whatsapp/transfer_service';
import { HTTP_STATUS } from '@/globals';
const transferService = new WhatsappTransferChatService();

export default {
    async agtWhatsTransferChatInitData (
        { commit },
        { campaingId = null, conversationId = null }
    ) {
        try {
            if (!campaingId || !conversationId) {
                await commit('agtWhatsTransferChatInitAgents', []);
                await commit('agtWhatsTransferChatInitCampaigns', []);
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener datos de transferencia'
                };
            }
            const [agentsResponse, campaignsResponse] = await Promise.all([
                transferService.getActiveAgents({ campaingId }),
                transferService.getActiveCampaigns({ conversationId })
            ]);
            const { status, data } = agentsResponse;
            await commit(
                'agtWhatsTransferChatInitAgents',
                status === HTTP_STATUS.SUCCESS ? data : []
            );
            await commit(
                'agtWhatsTransferChatInitCampaigns',
                campaignsResponse.status === HTTP_STATUS.SUCCESS ? campaignsResponse.data : []
            );
            return agentsResponse;
        } catch (error) {
            console.error('agtWhatsTransferChatInitData');
            console.error(error);
            await commit('agtWhatsTransferChatInitAgents', []);
            await commit('agtWhatsTransferChatInitCampaigns', []);
        }
    },
    async agtWhatsTransferChatSend ({ commit }, postData) {
        const serviceResponse = postData.targetType === 'campaign'
            ? await transferService.transferToCampaign(postData)
            : await transferService.transferToagent(postData);
        const { status } = serviceResponse;
        if (status === HTTP_STATUS.SUCCESS) {
            return {
                status: HTTP_STATUS.SUCCESS,
                message: postData.targetType === 'campaign'
                    ? 'Se transfirio satisfactoriamente el chat a la campaña'
                    : 'Se transfirio satisfactoriamente el chat'
            };
        } else {
            return {
                status: HTTP_STATUS.ERROR,
                message: postData.targetType === 'campaign'
                    ? 'No se pudo transferir el chat a la campaña'
                    : 'No se pudo transferir el chat'
            };
        }
    }
};
