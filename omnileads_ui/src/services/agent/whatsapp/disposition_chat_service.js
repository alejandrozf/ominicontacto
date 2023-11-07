import URLS from '@/api_urls/agent/whatsapp/disposition_chat_urls';
import { BaseService, HTTP } from '@/services/base_service';

class WhatsappDispositionChatService extends BaseService {
    constructor () {
        super(URLS, 'Whatsapp < Disposition Chat >');
    }

    async history ({ id }) {
        try {
            const resp = await fetch(
                this.urls.DispositionChatHistory(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener Historial de las calificaciones`);
            return [];
        } finally {
            this.initPayload();
        }
    }

    async options ({ campaignId }) {
        try {
            const resp = await fetch(
                this.urls.DispositionChatOptions(campaignId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener opciones de calificacion`);
            return [];
        } finally {
            this.initPayload();
        }
    }

    async detail ({ id }) {
        try {
            const resp = await fetch(
                this.urls.DispositionChatDetail(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener el detalle de la calificacion`);
            return null;
        } finally {
            this.initPayload();
        }
    }

    async create ({ data }) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                this.urls.DispositionChatCreate(),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`===> ERROR al crear la calificacion del chat`);
            console.error(error);
            return null;
        } finally {
            this.initPayload();
        }
    }

    async update ({ id, data }) {
        try {
            this.setPayload(HTTP.PUT, JSON.stringify(data));
            const resp = await fetch(
                this.urls.DispositionChatUpdate(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`===> ERROR al actualizar la calificacion del chat`);
            console.error(error);
            return null;
        } finally {
            this.initPayload();
        }
    }
}

export default new WhatsappDispositionChatService();
