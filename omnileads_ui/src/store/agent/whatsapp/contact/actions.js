/* eslint-disable no-unused-vars */
import Service from '@/services/agent/whatsapp/contact_service';
import { HTTP_STATUS } from '@/globals';
const service = new Service();
export default {
    async agtWhatsContactListInit ({ commit }, { campaignId = null, conversationId = null }) {
        try {
            if (!campaignId) {
                await commit('agtWhatsContactListInit', []);
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener contactos'
                };
            }
            const response = await service.getContacts({
                campaignId
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
    async agtContactCreateFromConversation (
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
            return await service.createContactFromConversation({
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
    async agtContactCreate(
        { commit },
        { campaignId = null, fdata }
    ) {
        try {
            if (!campaignId ) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al crear contacto'
                };
            }
            const response = await service.createContact({
                campaignId,
                fdata
            });
            const { status, data } = response;
            await commit('agtWhatsNewContact', status === HTTP_STATUS.SUCCESS ? data : []);
            return response
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
        { campaignId = null, contactId = null, data }
    ) {
        try {
            if (!campaignId || !contactId) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al actualizar contacto'
                };
            }
            return await service.updateContact({
                campaignId,
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
        { campaignId = null}
    ) {
        try {
            if (!campaignId) {
                await commit('agtWhatsContactDBFieldsInit', []);
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener los campos de la DB'
                };
            }
            const response = await service.getContactDBFields({
                campaignId
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
        { campaignId = null, filterData }
    ) {
        try {
            if (!campaignId) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al buscar contactos'
                };
            }
            const response = await service.searchOnContactDB({
                campaignId,
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
    },
};
