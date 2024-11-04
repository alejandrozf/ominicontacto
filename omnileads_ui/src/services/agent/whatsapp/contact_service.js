import URLS from '@/api_urls/agent/whatsapp/contact_urls';
import { BaseService, HTTP } from '@/services/base_service';

export default class WhatsappContactService extends BaseService {
    constructor () {
        super(URLS, 'Whatsapp <Contact>');
    }

    async getContacts ({ campaignId }) {
        try {
            const resp = await fetch(
                this.urls.ContactList(campaignId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener < Contactos >`);
            return [];
        } finally {
            this.initPayload();
        }
    }

    async searchOnContactDB ({ campaignId, data }) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                this.urls.ContactSearch(campaignId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al buscar en DB Contactos`);
            return null;
        } finally {
            this.initPayload();
        }
    }

    async getContactDBFields ({ campaignId }) {
        try {
            const resp = await fetch(
                this.urls.ContactCampaignDBFields(campaignId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener < Campos de la DB >`);
            return [];
        } finally {
            this.initPayload();
        }
    }

    async createContactFromConversation ({ campaignId, conversationId, data }) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                this.urls.ContactCreateFromConversation(campaignId, conversationId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`===> ERROR al crear Contacto`);
            console.error(error);
            return null;
        } finally {
            this.initPayload();
        }
    }

    async createContact ({ campaignId, fdata }) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(fdata));
            const resp = await fetch(
                this.urls.ContactCreate(campaignId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`===> ERROR al crear Contacto`);
            console.error(error);
            return null;
        } finally {
            this.initPayload();
        }
    }

    async updateContact ({ campaignId, contactId, data }) {
        try {
            this.setPayload(HTTP.PUT, JSON.stringify(data));
            const resp = await fetch(
                this.urls.ContactUpdate(campaignId, contactId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`===> ERROR al Actualizar Contacto`);
            console.error(error);
            return null;
        } finally {
            this.initPayload();
        }
    }
}
