/* eslint-disable no-unused-vars */
import Service from '@/services/agent/whatsapp/disposition_chat_service';
import { HTTP_STATUS } from '@/globals';
export default {
    async agtWhatsDispositionChatHistoryInit ({ commit }, { id = null }) {
        try {
            if (!id) {
                await commit('agtWhatsDispositionChatHistoryInit', []);
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener historial de calificaciones'
                };
            }
            const response = await Service.history({
                id
            });
            const { status, data } = response;
            await commit(
                'agtWhatsDispositionChatHistoryInit',
                status === HTTP_STATUS.SUCCESS ? data : []
            );
            return response;
        } catch (error) {
            console.error('===> ERROR al obtener historial de calificaciones');
            console.error(error);
            await commit('agtWhatsDispositionChatHistoryInit', []);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener historial de calificaciones'
            };
        }
    },
    async agtWhatsDispositionChatOptionsInit ({ commit }, { campaignId = null }) {
        try {
            if (!campaignId) {
                await commit('agtWhatsDispositionChatOptionsInit', []);
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener opciones de calificacion'
                };
            }
            const response = await Service.options({
                campaignId
            });
            const { status, data } = response;
            await commit(
                'agtWhatsDispositionChatOptionsInit',
                status === HTTP_STATUS.SUCCESS ? data : []
            );
            return response;
        } catch (error) {
            console.error('===> ERROR al obtener opciones de calificacion');
            console.error(error);
            await commit('agtWhatsDispositionChatOptionsInit', []);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener opciones de calificacion'
            };
        }
    },
    async agtWhatsDispositionChatDetailInit ({ commit }, { id = null }) {
        try {
            if (!id) {
                await commit('agtWhatsDispositionChatDetailInit', null);
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener el detalle de la calificacion'
                };
            }
            const response = await Service.detail({
                id
            });
            const { status, data } = response;
            await commit(
                'agtWhatsDispositionChatDetailInit',
                status === HTTP_STATUS.SUCCESS ? data : null
            );
            return response;
        } catch (error) {
            console.error('===> ERROR al obtener el detalle de la calificacion');
            console.error(error);
            await commit('agtWhatsDispositionChatDetailInit', null);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener el detalle de la calificacion'
            };
        }
    },
    async agtWhatsDispositionChatCreate (
        { commit },
        { data }
    ) {
        try {
            return await Service.create({
                data
            });
        } catch (error) {
            console.error('===> ERROR al crear calificacion');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al crear calificacion'
            };
        }
    },
    async agtWhatsDispositionChatUpdate (
        { commit },
        { id = null, data }
    ) {
        try {
            if (!id) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al actualizar calificacion'
                };
            }
            return await Service.update({
                id,
                data
            });
        } catch (error) {
            console.error('===> ERROR al actualizar calificacion');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al actualizar calificacion'
            };
        }
    },
    agtWhatsDispositionChatSetFormFlag (
        { commit },
        flag = true
    ) {
        commit('agtWhatsDispositionChatSetFormFlag', flag);
    }
};
