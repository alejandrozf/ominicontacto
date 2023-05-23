import urls from '@/api_urls/agent/whatsapp/management_urls';
import { BaseService } from '@/services/base_service';

export default class WhatsappManagementService extends BaseService {
    constructor () {
        super(urls, 'Whatsapp Agente <Gestion de Formulario>');
    }

    // async getMessagesByConversationId (id) {
    //     try {
    //         const resp = await fetch(this.urls.Campaigns, this.payload);
    //         return await resp.json();
    //     } catch (error) {
    //         console.error(`Error al obtener < Mensajes de la Conversacion >`);
    //         return [];
    //     } finally {
    //         this.initPayload();
    //     }
    // }
}
