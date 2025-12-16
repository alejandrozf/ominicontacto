import urls from '@/api_urls/supervisor/facebook/templates_urls';
import { BaseService } from '@/services/base_service';

export default class FacebookTemplateService extends BaseService {
    constructor () {
        super(urls, 'Templates');
    }

    async getTemplates (campaignId, pageId = null) {
        try {
            const resp = await fetch(
                this.urls.Templates(campaignId, pageId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener < Facebook Templates >`);
            console.error(error);
            return [];
        } finally {
            this.initPayload();
        }
    }
}
