import urls from '@/api_urls/supervisor/whatsapp/configuration_campaign_urls';
import { BaseService } from '@/services/base_service';

export default class WhatsappConfigurationCampaignService extends BaseService {
    constructor () {
        super(urls, 'Whatsapp Configuracion Campaign');
    }

    async campaignTemplatesInit (campaignId) {
        try {
            const resp = await fetch(this.urls.CampaignTemplates(campaignId), this.payload);
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener < Templates de la Campana ${campaignId} >`);
            return [];
        } finally {
            this.initPayload();
        }
    }
}
