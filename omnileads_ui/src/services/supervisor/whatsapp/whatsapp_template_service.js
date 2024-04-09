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

    async changeStatus ({ templateId, lineId }) {
        try {
            const resp = await fetch(this.urls.StatusChange(templateId, lineId), this.payload);
            return await resp.json();
        } catch (error) {
            console.error(`Error al cambiar status de < Whatsapp Templates >`);
            return {
                status: false,
                message: 'Error al cambiar status de Whatsapp Templates'
            };
        } finally {
            this.initPayload();
        }
    }
}
