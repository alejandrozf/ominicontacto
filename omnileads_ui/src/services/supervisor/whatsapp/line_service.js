import urls from '@/api_urls/supervisor/whatsapp/line_urls';
import { BaseService } from '@/services/base_service';

export default class LineService extends BaseService {
    constructor () {
        super(urls, 'Linea de WhatsApp');
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
