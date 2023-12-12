import URLS from '@/api_urls/supervisor/whatsapp/reports/general_report_urls';
import { BaseService, HTTP } from '@/services/base_service';

export default class SupWhatsReportGeneralService extends BaseService {
    constructor () {
        super(URLS, 'Whatsapp <General Report>');
    }

    async getGeneralWhatsappReport ({
        campaignId = null,
        filters = { startDate: null, endDate: null }
    }) {
        try {
            this.setPayload(
                HTTP.POST,
                JSON.stringify({
                    start_date: filters.startDate,
                    end_date: filters.endDate,
                    campaign: campaignId
                })
            );
            const url = this.urls.SupWhatsReportGeneral();
            const resp = await fetch(url, this.payload);
            return await resp.json();
        } catch (error) {
            console.error(
                `Error al obtener < Reporte General de Whatsapp de la Campana (${campaignId}) >`
            );
            return [];
        } finally {
            this.initPayload();
        }
    }
}
