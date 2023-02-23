import urls from '@/api_urls/supervisor/whatsapp/whatsapp_template_urls';
import { BaseService } from '@/services/base_service';

export default class WhatsappTemplateService extends BaseService {
    constructor () {
        super(urls, 'Whatsapp Template');
    }

    async sycnUp (lineId) {
        try {
            const resp = await fetch(this.urls.SyncUp(lineId), this.payload);
            return await resp.json();
        } catch (error) {
            console.error(`Error al sincronizar < Whatsapp Templates >`);
            return [];
        } finally {
            this.initPayload();
        }
    }
}
