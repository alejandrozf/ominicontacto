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

    async sendAttachmentMessage (chatId, data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
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

    async getAgentChatsList () {
        try {
            const resp = await fetch(this.urls.ChatAgentConversationsList(), this.payload);
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener < Lista de Chats >`);
            return [];
        } finally {
            this.initPayload();
        }
    }
}
