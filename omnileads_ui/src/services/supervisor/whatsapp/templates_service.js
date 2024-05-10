import urls from '@/api_urls/supervisor/whatsapp/templates_urls';
import { BaseService } from '@/services/base_service';

export default class WhatsappTemplateService extends BaseService {
    constructor () {
        super(urls, 'Templates');
    }

    async getTemplates (campaignId, lineId = null) {
        try {
            const resp = await fetch(
                this.urls.Templates(campaignId, lineId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener < Whatsapp Templates >`);
            console.error(error);
            return [];
        } finally {
            this.initPayload();
        }
    }
}
