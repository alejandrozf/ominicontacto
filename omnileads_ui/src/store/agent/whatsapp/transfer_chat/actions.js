/* eslint-disable no-unused-vars */
import AgentService from '@/services/supervisor/agents_campaign_service';
// import Service from '@/services/agent/whatsapp/management_service';
const agentService = new AgentService();
// const service = new Service();

export default {
    async agtWhatsTransferChatInitData ({ commit }, conversationId) {
        try {
            const { activeAgents, status } = await agentService.getActiveAgents();
            await commit('agtWhatsTransferChatInitAgents', status === 'SUCCESS' ? activeAgents : []);
            const data = {
                from: 20,
                to: null,
                conversationId
            };
            await commit('agtWhatsTransferChatInitData', data);
        } catch (error) {
            console.error('agtWhatsTransferChatInitData');
            console.error(error);
            await commit('agtWhatsTransferChatInitAgents', []);
            await commit('agtWhatsTransferChatInitData', {
                from: null,
                to: null,
                conversationId: null
            });
        }
    },
    agtWhatsTransferChatSend ({ commit }, data) {
        // return await service.create(data);
        console.log('Transfer Chat');
        console.log(data);
        return {
            status: 'SUCCESS',
            message: 'Se transfirio satisfactoriamente el chat'
        };
    }
};
