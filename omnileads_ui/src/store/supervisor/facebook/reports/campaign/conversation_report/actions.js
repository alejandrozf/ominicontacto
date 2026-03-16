/* eslint-disable no-unused-vars */
import { HTTP_STATUS } from '@/globals';
import Service from '@/services/supervisor/facebook/reports/campaign/conversation_report_service';
const service = new Service();

export default {
    async initSupFacebookReportCampaignConversations (
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
                await service.getCampaignReportConversations({
                    campaignId,
                    filters
                });
            commit(
                'initSupFacebookReportCampaignConversations',
                status === HTTP_STATUS.SUCCESS ? data : []
            );
        } catch (error) {
            console.error(
                `===> Error al obtener < Reporte de Conversaciones Meta/Facebook de la Campana (${campaignId}) >`
            );
            console.error(error);
            commit('initSupFacebookReportCampaignConversations', []);
        }
    },
    async initSupFacebookReportCampaignAgents ({ commit }, { campaignId = null }) {
        try {
            const { status, agentsCampaign } =
                await service.getCampaignReportAgents({
                    campaignId
                });
            commit(
                'initSupFacebookReportCampaignAgents',
                status === HTTP_STATUS.SUCCESS ? agentsCampaign : []
            );
        } catch (error) {
            console.error(
                `===> Error al obtener < Agentes de la Campana (${campaignId}) para Meta/Facebook >`
            );
            console.error(error);
            commit('initSupFacebookReportCampaignAgents', []);
        }
    }
};
