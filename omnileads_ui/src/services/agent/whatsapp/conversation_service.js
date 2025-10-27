import URLS from '@/api_urls/agent/whatsapp/conversation_urls';
import { BaseService, HTTP } from '@/services/base_service';

export default class WhatsappConversationService extends BaseService {
    constructor () {
        super(URLS, 'Whatsapp <Conversation>');
    }

    async getMessagesByConversationId (chatId) {
        try {
            const resp = await fetch(this.urls.ChatMessages(chatId), this.payload);
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener < Mensajes de la Conversacion >`);
            return [];
        } finally {
            this.initPayload();
        }
    }

    async getConversationDetail (chatId) {
        try {
            this.initPayload();
            const resp = await fetch(this.urls.ChatAgentConversationsDetail(chatId), this.payload);
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener < Detalle de la Conversacion >`);
            return [];
        } finally {
            this.initPayload();
        }
    }

    async sendTextMessage (chatId, data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                this.urls.ChatSendTextMessage(chatId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al enviar Mensaje de Texto`);
            return null;
        } finally {
            this.initPayload();
        }
    }

    async sendAttachmentMessage (chatId, formData) {
        try {
            this.setPayload(HTTP.POST, formData, true);
            const resp = await fetch(
                this.urls.ChatSendAttachmentMessage(chatId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al enviar Mensaje Multimedia`);
            return null;
        } finally {
            this.initPayload();
        }
    }

    async sendTemplateMessage (chatId, data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                this.urls.ChatSendTemplateMessage(chatId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al enviar Template de Mensaje`);
            return null;
        } finally {
            this.initPayload();
        }
    }

    async sendWhatsappTemplateMessage (chatId, data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                this.urls.ChatSendWhatsappTemplateMessage(chatId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al enviar Whatsapp Template de Mensaje`);
            return null;
        } finally {
            this.initPayload();
        }
    }

    async reactiveExpiredConversation (chatId, data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                this.urls.ChatAgentReactiveExpiredConversation(chatId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al reactivar la conversacion expirada`);
            return null;
        } finally {
            this.initPayload();
        }
    }

    async getAgentChatsList () {
        try {
            this.initPayload();
            const resp = await fetch(this.urls.ChatAgentConversationsList(), this.payload);
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener < Lista de Chats >`);
            return [];
        } finally {
            this.initPayload();
        }
    }

    async requestConversation ({ id, data = {} }) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                this.urls.ChatAgentConversationRequest(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`ERROR al solicitar Conversacion (${id})`);
            return null;
        } finally {
            this.initPayload();
        }
    }

    async initNewConversation (data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                this.urls.ChatAgentNewConversation(),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al iniciar nueva conversacion`);
            return {
                success: false,
                message: 'Error al iniciar nueva conversacion'
            };
        } finally {
            this.initPayload();
        }
    }

    async markMessageAsRead (data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                this.urls.ChatMarkAsRead(),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al marcar como leido el mensaje`);
            return {
                success: false,
                message: 'Error inesperado'
            };
        } finally {
            this.initPayload();
        }
    }
}
