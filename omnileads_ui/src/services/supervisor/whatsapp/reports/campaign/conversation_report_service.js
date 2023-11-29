import URLS from '@/api_urls/supervisor/whatsapp/reports/campaign/conversation_report_urls';
import { BaseService, HTTP } from '@/services/base_service';

export default class SupWhatsReportCampaignConversationService extends BaseService {
    constructor () {
        super(URLS, 'Whatsapp <Campaign Conversation Report>');
    }

    async getCampaingReportConversations ({
        campaignId = null,
        filters = { startDate: null, endDate: null, phone: null, agents: null }
    }) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify({
                start_date: filters.startDate,
                end_date: filters.endDate,
                phone: filters.phone,
                agents: filters.agents
            }));
            const url =
                this.urls.SupWhatsReportCampaignConversations(campaignId);
            const resp = await fetch(url, this.payload);
            return await resp.json();
        } catch (error) {
            console.error(
                `Error al obtener < Reporte de Conversaciones de la Campana (${campaignId}) >`
            );
            return [];
        } finally {
            this.initPayload();
        }
    }

    async getCampaingReportAgents ({ campaignId = null }) {
        try {
            const url = this.urls.SupWhatsReportCampaignAgents(campaignId);
            const resp = await fetch(url, this.payload);
            return await resp.json();
        } catch (error) {
            console.error(
                `Error al obtener < Agentes de la Campana (${campaignId}) >`
            );
            return [];
        } finally {
            this.initPayload();
        }
    }
}
