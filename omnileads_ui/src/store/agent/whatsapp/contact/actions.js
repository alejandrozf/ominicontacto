/* eslint-disable no-unused-vars */
import Service from '@/services/agent/whatsapp/contact_service';
import { HTTP_STATUS } from '@/globals';
const service = new Service();
export default {
    async agtWhatsContactListInit ({ commit }, { campaignId = null, conversationId = null }) {
        try {
            if (!campaignId || !conversationId) {
                await commit('agtWhatsContactListInit', []);
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener contactos'
                };
            }
            const response = await service.getContacts({
                campaignId,
                conversationId
            });
            const { status, data } = response;
            await commit(
                'agtWhatsContactListInit',
                status === HTTP_STATUS.SUCCESS ? data : []
            );
            return response;
        } catch (error) {
            console.error('===> ERROR al obtener contactos');
            console.error(error);
            await commit('agtWhatsContactListInit', []);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener contactos'
            };
        }
    },
    async agtWhatsContactCreate (
        { commit },
        { campaignId = null, conversationId = null, data }
    ) {
        try {
            if (!campaignId || !conversationId) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al crear contacto'
                };
            }
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
        { campaignId = null, conversationId = null, contactId = null, data }
    ) {
        try {
            if (!campaignId || !conversationId || !contactId) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al actualizar contacto'
                };
            }
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
                message: 'Error al actualizar contacto'
            };
        }
    },
    async agtWhatsContactDBFieldsInit (
        { commit },
        { campaignId = null, conversationId = null }
    ) {
        try {
            if (!campaignId || !conversationId) {
                await commit('agtWhatsContactDBFieldsInit', []);
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener los campos de la DB'
                };
            }
            const response = await service.getContactDBFields({
                campaignId,
                conversationId
            });
            const { status, data } = response;
            await commit('agtWhatsContactDBFieldsInit', status === HTTP_STATUS.SUCCESS ? data : []);
            return response;
        } catch (error) {
            console.error('===> ERROR al obtener los campos de la DB');
            console.error(error);
            await commit('agtWhatsContactDBFieldsInit', []);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener los campos de la DB'
            };
        }
    },
    async agtWhatsContactSearch (
        { commit },
        { campaignId = null, conversationId = null, filterData }
    ) {
        try {
            if (!campaignId || !conversationId) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al buscar contactos'
                };
            }
            const response = await service.searchOnContactDB({
                campaignId,
                conversationId,
                data: filterData
            });
            const { status, data } = response;
            await commit('agtWhatsContactSearchInit', status === HTTP_STATUS.SUCCESS ? data : []);
            return response;
        } catch (error) {
            console.error('===> ERROR al buscar los contactos');
            console.error(error?.message);
            await commit('agtWhatsContactSearchInit', []);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al buscar contactos'
            };
        }
    }
};
