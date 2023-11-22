/* eslint-disable no-unused-vars */
import Service from '@/services/agent/whatsapp/disposition_chat_service';
import { HTTP_STATUS } from '@/globals';
export default {
    async agtWhatsDispositionChatHistoryInit ({ commit }, { id = null }) {
        try {
            if (!id) {
                await commit('agtWhatsDispositionChatHistoryInit', []);
                return;
            }
            const { status, data } = await Service.history({
                id
            });
            await commit(
                'agtWhatsDispositionChatHistoryInit',
                status === HTTP_STATUS.SUCCESS ? data : []
            );
        } catch (error) {
            console.error('===> ERROR al obtener historial de calificaciones');
            console.error(error);
            await commit('agtWhatsDispositionChatHistoryInit', []);
        }
    },
    async agtWhatsDispositionChatOptionsInit ({ commit }, { campaignId = null }) {
        try {
            if (!campaignId) {
                await commit('agtWhatsDispositionChatOptionsInit', []);
                return;
            }
            const { status, data } = await Service.options({
                campaignId
            });
            await commit(
                'agtWhatsDispositionChatOptionsInit',
                status === HTTP_STATUS.SUCCESS ? data : []
            );
        } catch (error) {
            console.error('===> ERROR al obtener opciones de calificacion');
            console.error(error);
            await commit('agtWhatsDispositionChatOptionsInit', []);
        }
    },
    async agtWhatsDispositionChatDetailInit ({ commit }, { id = null }) {
        try {
            if (!id) {
                await commit('agtWhatsDispositionChatDetailInit', null);
                return;
            }
            const { status, data } = await Service.detail({
                id
            });
            await commit(
                'agtWhatsDispositionChatDetailInit',
                status === HTTP_STATUS.SUCCESS ? data : null
            );
        } catch (error) {
            console.error('===> ERROR al obtener el detalle de la calificacion');
            console.error(error);
            await commit('agtWhatsDispositionChatDetailInit', null);
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
        { id, data }
    ) {
        try {
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
