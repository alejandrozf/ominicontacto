/* eslint-disable no-unused-vars */
import Service from '@/services/agent/whatsapp/contact_service';
import { HTTP_STATUS } from '@/globals';
const service = new Service();
export default {
    async agtWhatsContactList ({ commit }, { campaignId, conversationId }) {
        try {
            const { status, data } = await service.getContacts({
                campaignId,
                conversationId
            });
            await commit(
                'agtWhatsContactListInit',
                status === HTTP_STATUS.SUCCESS ? data : []
            );
        } catch (error) {
            console.error('===> ERROR al obtener contactos');
            console.error(error);
            await commit('agtWhatsContactListInit', []);
        }
    },
    async agtWhatsContactCreate (
        { commit },
        { campaignId, conversationId, data }
    ) {
        try {
            return await service.createContact({
                campaignId,
                conversationId,
                data
            });
        } catch (error) {
            console.error('===> ERROR to create contact');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al crear contacto'
            };
        }
    },
    async agtWhatsContactUpdate (
        { commit },
        { campaignId, conversationId, contactId, data }
    ) {
        try {
            return await service.updateContact({
                campaignId,
                conversationId,
                contactId,
                data
            });
        } catch (error) {
            console.error('===> ERROR to update contact');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al crear contacto'
            };
        }
    },
    async agtWhatsContactDBFieldsInit (
        { commit },
        { campaignId, conversationId }
    ) {
        try {
            const { status, data } = await service.getContactDBFields({
                campaignId,
                conversationId
            });
            if (status === HTTP_STATUS.SUCCESS) {
                await commit('agtWhatsContactDBFieldsInit', data);
            }
        } catch (error) {
            console.error('===> ERROR al obtener los campos de la DB');
            console.error(error);
            await commit('agtWhatsContactDBFieldsInit', []);
        }
    },
    async agtWhatsContactSearch (
        { commit },
        { campaignId, conversationId, data }
    ) {
        try {
            return await service.searchOnContactDB({
                campaignId,
                conversationId,
                data
            });
        } catch (error) {
            console.error('===> ERROR al obtener los campos de la DB');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al crear contacto'
            };
        }
    }
};
