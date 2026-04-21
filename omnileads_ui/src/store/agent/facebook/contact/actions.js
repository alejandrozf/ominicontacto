/* eslint-disable no-unused-vars */
import Service from '@/services/agent/facebook/contact_service';
import { HTTP_STATUS } from '@/globals';
const service = new Service();
export default {
    async agtFacebookContactListInit ({ commit }, { campaignId = null, conversationId = null }) {
        try {
            if (!campaignId) {
                await commit('agtFacebookContactListInit', []);
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
                'agtFacebookContactListInit',
                status === HTTP_STATUS.SUCCESS ? data : []
            );
            return response;
        } catch (error) {
            console.error('===> ERROR al obtener contactos');
            console.error(error);
            await commit('agtFacebookContactListInit', []);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener contactos'
            };
        }
    },
    async agtFacebookContactCreateFromConversation (
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
    async agtFacebookContactCreate (
        { commit },
        { campaignId = null, fdata }
    ) {
        try {
            if (!campaignId) {
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
            await commit('agtFacebookNewContact', status === HTTP_STATUS.SUCCESS ? data : []);
            return response;
        } catch (error) {
            console.error('===> ERROR to create contact');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al crear contacto'
            };
        }
    },
    async agtFacebookContactUpdate (
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
    async agtFacebookContactDBFieldsInit (
        { commit },
        { campaignId = null }
    ) {
        console.log('agtFacebookContactDBFieldsInit action', campaignId);
        try {
            if (!campaignId) {
                await commit('agtFacebookContactDBFieldsInit', []);
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener los campos de la DB'
                };
            }
            const response = await service.getContactDBFields({
                campaignId
            });
            const { status, data } = response;
            await commit('agtFacebookContactDBFieldsInit', status === HTTP_STATUS.SUCCESS ? data : []);
            return response;
        } catch (error) {
            console.error('===> ERROR al obtener los campos de la DB');
            console.error(error);
            await commit('agtFacebookContactDBFieldsInit', []);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener los campos de la DB'
            };
        }
    },
    async agtFacebookContactSearch (
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
            await commit('agtFacebookContactSearchInit', status === HTTP_STATUS.SUCCESS ? data : []);
            return response;
        } catch (error) {
            console.error('===> ERROR al buscar los contactos');
            console.error(error?.message);
            await commit('agtFacebookContactSearchInit', []);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al buscar contactos'
            };
        }
    },
    async agtFacebookContactSuggestMatch (
        { commit },
        { campaignId = null, conversationId = null }
    ) {
        try {
            if (!campaignId || !conversationId) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al sugerir coincidencia de contacto'
                };
            }
            return await service.suggestMatch({
                campaignId,
                conversationId
            });
        } catch (error) {
            console.error('===> ERROR al sugerir coincidencia de contacto');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al sugerir coincidencia de contacto'
            };
        }
    },
    async agtFacebookContactAssignToConversation (
        { commit },
        { conversationId = null, contactId = null }
    ) {
        try {
            if (!conversationId || !contactId) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al asignar el contacto'
                };
            }
            return await service.assignContactToConversation({
                conversationId,
                contactId
            });
        } catch (error) {
            console.error('===> ERROR al asignar contacto a la conversación');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al asignar el contacto'
            };
        }
    }
};
