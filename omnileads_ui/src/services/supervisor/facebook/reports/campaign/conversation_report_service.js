import URLS from '@/api_urls/supervisor/facebook/reports/campaign/conversation_report_urls';
import { BaseService, HTTP } from '@/services/base_service';

export default class SupFacebookReportCampaignConversationService extends BaseService {
    constructor () {
        super(URLS, 'Meta/Facebook <Campaign Conversation Report>');
    }

    normalizeDate (date) {
        if (!date) {
            return null;
        }
        if (typeof date === 'string') {
            return date.slice(0, 10);
        }
        const month = `${date.getMonth() + 1}`.padStart(2, '0');
        const day = `${date.getDate()}`.padStart(2, '0');
        return `${date.getFullYear()}-${month}-${day}`;
    }

    async getCampaignReportConversations ({
        campaignId = null,
        filters = { startDate: null, endDate: null, phone: null, agents: null }
    }) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify({
                start_date: this.normalizeDate(filters.startDate),
                end_date: this.normalizeDate(filters.endDate),
                phone: filters.phone,
                agents: filters.agents
            }));
            const url = this.urls.SupFacebookReportCampaignConversations(campaignId);
            const resp = await fetch(url, this.payload);
            return await resp.json();
        } catch (error) {
            console.error(
                `Error al obtener < Reporte de Conversaciones Meta/Facebook de la Campana (${campaignId}) >`
            );
            return [];
        } finally {
            this.initPayload();
        }
    }

    async getCampaignReportAgents ({ campaignId = null }) {
        try {
            const url = this.urls.SupFacebookReportCampaignAgents(campaignId);
            const resp = await fetch(url, this.payload);
            return await resp.json();
        } catch (error) {
            console.error(
                `Error al obtener < Agentes de la Campana (${campaignId}) para Meta/Facebook >`
            );
            return [];
        } finally {
            this.initPayload();
        }
    }
}
