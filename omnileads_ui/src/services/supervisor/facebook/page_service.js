import urls from '@/api_urls/supervisor/facebook/page_urls';
import { BaseService } from '@/services/base_service';

export default class PageService extends BaseService {
    constructor () {
        super(urls, 'Page de Facebook');
    }

    async getCampaigns () {
        try {
            const resp = await fetch(this.urls.Campaigns, this.payload);
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener < Campanas >`);
            return [];
        } finally {
            this.initPayload();
        }
    }
}
