/* eslint-disable no-unused-vars */
import { HTTP_STATUS } from '@/globals';
import Service from '@/services/supervisor/whatsapp/reports/campaign/conversation_report_service';
const service = new Service();

export default {
    async initSupWhatsReportCampaignConversations (
        { commit },
        {
            campaignId = null,
            filters = {
                startDate: null,
                endDate: null,
                phone: null,
                agents: null
            }
        }
    ) {
        try {
            const { status, data } =
                await service.getCampaingReportConversations({
                    campaignId,
                    filters
                });
            commit(
                'initSupWhatsReportCampaignConversations',
                status === HTTP_STATUS.SUCCESS ? data : []
            );
        } catch (error) {
            console.error(
                `===> Error al obtener < Reporte de Conversaciones de la Campana (${campaignId}) >`
            );
            console.error(error);
            commit('initSupWhatsReportCampaignConversations', []);
        }
    },
    async initSupWhatsReportCampaignAgents ({ commit }, { campaignId = null }) {
        try {
            const { status, agentsCampaign } =
                await service.getCampaingReportAgents({
                    campaignId
                });
            commit(
                'initSupWhatsReportCampaignAgents',
                status === HTTP_STATUS.SUCCESS ? agentsCampaign : []
            );
        } catch (error) {
            console.error(
                `===> Error al obtener < Agentes de la Campana (${campaignId}) >`
            );
            console.error(error);
            commit('initSupWhatsReportCampaignAgents', []);
        }
    }
};
