import urls from '@/api_urls/supervisor/whatsapp/whatsapp_template_urls';
import { BaseService } from '@/services/base_service';

export default class FacebookTemplateService extends BaseService {
    constructor () {
        super(urls, 'Facebook Template');
    }

    async syncUp (lineId) {
        try {
            const resp = await fetch(this.urls.SyncUp(lineId), this.payload);
            return await resp.json();
        } catch (error) {
            console.error(`Error al sincronizar < Facebook Templates >`);
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
