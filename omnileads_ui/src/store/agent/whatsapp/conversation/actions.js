/* eslint-disable */
import Service from '@/services/agent/whatsapp/conversation_service';
import { HTTP_STATUS } from '@/globals';
import { resetStoreDataByAction } from '@/utils';
const service = new Service();

const getMessageInfo = ({ $t, data = null, itsMine = true }) => {
    const senderName = data && data.sender && data.sender.name ? data.sender.name : null;
    const senderPhone = data && data.sender && data.sender.phone ? data.sender.phone : $t('globals.whatsapp.automatic_agent');
    const clientName =  data && data.contact_data && data.contact_data && data.contact_data.data && data.contact_data.data.nombre ? data.contact_data.data.nombre : null;
    return {
        id: data.id,
        from: itsMine ? `${$t('globals.agent')} (${senderName || senderPhone})` : clientName || senderName || senderPhone,
        conversationId: data && data.conversation ? data.conversation : null,
        itsMine,
        message: data && data.content && data.content ? data.content : '',
        status: data && data.status ? data.status : null,
        fail_reason: data && data.fail_reason ? data.fail_reason : null,
        date: data && data.timestamp ? new Date(data.timestamp) : null,
        type: data && data.type ? data.type : null,
    };
};

export default {
    async agtWhatsCoversationSendAttachmentMessage (
        { commit },
        { conversationId = null, formData, phoneLine = null, messages, $t}
    ) {
        try {
            if (!conversationId || !formData.get('file')) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al enviar mensaje multimedia'
                };
            }
            const response = await service.sendAttachmentMessage(
                conversationId,
                formData
            );
            const { status, data } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                const itsMine = data.origin === phoneLine;
                const message = getMessageInfo({ $t, data, itsMine });
                messages.push(message);
                await commit('agtWhatsCoversationSendMessage', message);
            }
            await resetStoreDataByAction({
                action: 'agtWhatsSetCoversationMessages',
                data: messages
            });
            return response;
        } catch (error) {
            console.error('===> ERROR al enviar mensaje multimedia');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al enviar mensaje multimedia'
            };
        }
    },
    async agtWhatsCoversationSendTextMessage (
        { commit },
        { conversationId = null, message = null, phoneLine = null, $t }
    ) {
        try {
            if (!conversationId || !message || !phoneLine) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al enviar mensaje de Texto'
                };
            }
            const response = await service.sendTextMessage(conversationId, {
                message: message ? message.message : '',
                destination: message.destination ? message.destination : '',
                type: 'text'
            });
            const { status, data } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                const itsMine = data.origin === phoneLine;
                const message = getMessageInfo({ $t, data, itsMine });
                await commit('agtWhatsCoversationSendMessage', message);
            }
            return response;
        } catch (error) {
            console.error('===> ERROR al enviar mensaje de texto');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al enviar mensaje de Texto'
            };
        }
    },
    async agtWhatsCoversationSendTemplateMessage (
        { commit },
        { conversationId = null, templateId = null, phoneLine = null, messages = null, $t }
    ) {
        try {
            if (!conversationId || !templateId || !phoneLine) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al enviar template de Texto'
                };
            }
            const result = await service.sendTemplateMessage(conversationId, {
                template_id: templateId
            });
            const { status, data } = result;
            if (status === HTTP_STATUS.SUCCESS) {
                const itsMine = data.origin === phoneLine;
                const message = getMessageInfo({ $t, data, itsMine });
                messages.push(message);
            }
            await resetStoreDataByAction({
                action: 'agtWhatsSetCoversationMessages',
                data: messages
            });
            await commit('agtWhatsConversationInitMessages', messages);
            return result;
        } catch (error) {
            console.error('===> ERROR al enviar template de texto');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al enviar template de Texto'
            };
        }
    },
    async agtWhatsCoversationSendWhatsappTemplateMessage (
        { commit },
        { conversationId = null, templateId = null, params, phoneLine, messages, $t }
    ) {
        try {
            if (!conversationId || !templateId) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al enviar Template de Whatsapp'
                };
            }
            const result = await service.sendWhatsappTemplateMessage(
                conversationId,
                { template_id: templateId, params }
            );
            const { status, data } = result;
            if (status === HTTP_STATUS.SUCCESS) {
                const itsMine = data.origin === phoneLine;
                const message = getMessageInfo({ $t, data, itsMine });
                messages.push(message);
            }
            await resetStoreDataByAction({
                action: 'agtWhatsSetCoversationMessages',
                data: messages
            });
            return result;
        } catch (error) {
            console.error('===> ERROR al enviar Template de Whatsapp');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al enviar Template de Whatsapp'
            };
        }
    },
    async agtWhatsCoversationReactiveExpiredConversation (
        { commit },
        { conversationId = null, templateId = null, params, phoneLine, messages, $t }
    ) {
        try {
            if (!conversationId || !templateId) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al reactivar conversacion expirada'
                };
            }
            const result = await service.reactiveExpiredConversation(
                conversationId,
                { template_id: templateId, params }
            );
            const { status, data } = result;
            if (status === HTTP_STATUS.SUCCESS) {
                const itsMine = data.origin === phoneLine;
                const message = getMessageInfo({ $t, data, itsMine });
                messages.push(message);
            }
            await resetStoreDataByAction({
                action: 'agtWhatsSetCoversationMessages',
                data: messages
            });
            await resetStoreDataByAction({
                action: 'agtWhatsCoversationDetailInit',
                data: null
            });
            return result;
        } catch (error) {
            console.error('===> ERROR al reactivar conversacion expirada');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al reactivar conversacion expirada'
            };
        }
    },
    agtWhatsCoversationReciveMessage ({ commit }, message) {
        try {
            commit('agtWhatsCoversationReciveMessage', message);
        } catch (error) {
            console.error('===> ERROR al recibir mensaje de texto');
            console.error(error);
        }
    },
    async agtWhatsConversationDetail ({ commit }, { conversationId = null, $t }) {
        try {
            if (!conversationId) {
                commit('agtWhatsConversationInitMessages', []);
                commit('agtWhatsConversationInfoInit', {});
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener detalle de la conversacion'
                };
            }
            const { status, data } = await service.getConversationDetail(
                conversationId
            );
            if (status === HTTP_STATUS.SUCCESS) {
                commit(
                    'agtWhatsConversationInitMessages',
                    data.messages.map((msg) => {
                        const itsMine = msg.origin === data.line.number;
                        return getMessageInfo({ $t, data: msg, itsMine });
                    })
                );
                commit('agtWhatsConversationInfoInit', data);
            }
        } catch (error) {
            console.error('===> ERROR al obtener detalle de la conversacion');
            console.error(error);
            commit('agtWhatsConversationInitMessages', []);
            commit('agtWhatsConversationInfoInit', {});
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener detalle de la conversacion'
            };
        }
    },
    async agtWhatsChatsListInit ({ commit }) {
        try {
            const { status, data } = await service.getAgentChatsList();
            commit('agtWhatsChatsListInit', {
                isNew:
                    status === HTTP_STATUS.SUCCESS
                        ? data.new_conversations
                        : [],
                inProgress:
                    status === HTTP_STATUS.SUCCESS
                        ? data.inprogress_conversations
                        : []
            });
        } catch (error) {
            console.error(
                '===> ERROR al obtener la lista de chats de un agente'
            );
            console.error(error);
            commit('agtWhatsChatsListInit', { isNew: [], inProgress: [] });
        }
    },
    agtWhatsReceiveNewChat ({ commit }, chat = null) {
        try {
            commit('agtWhatsReceiveNewChat', chat);
        } catch (error) {
            console.error('===> ERROR al recibir nuevo chat');
            console.error(error);
            commit('agtWhatsReceiveNewChat', null);
        }
    },
    async agtWhatsCoversationRequest ({ commit }, conversationId = null) {
        try {
            if (!conversationId) {
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al pedir una conversacion'
                };
            }
            return await service.requestConversation({
                id: conversationId
            });
        } catch (error) {
            console.error('===> ERROR al pedir una conversacion');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al pedir una conversacion'
            };
        }
    },
    agtWhatsSetCoversationMessages ({ commit }, messages = []) {
        try {
            commit('agtWhatsConversationInitMessages', messages);
        } catch (error) {
            console.error('===> ERROR al settear Mensajes de la conversacion');
            console.error(error);
            commit('agtWhatsConversationInitMessages', []);
        }
    },
    agtWhatsSetCoversationInfo ({ commit }, info = null) {
        try {
            commit('agtWhatsSetCoversationInfo', info);
        } catch (error) {
            console.error('===> ERROR al settear info de la conversacion');
            console.error(error);
            commit('agtWhatsSetCoversationInfo', null);
        }
    },
    agtWhatsRestartExpiredCoversation ({ commit }, info = null) {
        try {
            commit('agtWhatsRestartExpiredCoversation', info);
        } catch (error) {
            console.error(
                '===> ERROR al actualizar la fecha de expiracion de la conversacion'
            );
            console.error(error);
            commit('agtWhatsRestartExpiredCoversation', null);
        }
    },
    async agtWhatsInitNewConversation ({ commit }, data) {
        try {
            return await service.initNewConversation(data);
        } catch (error) {
            console.error('===> ERROR al iniciar nueva conversacion');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al iniciar nueva conversacion'
            };
        }
    }
};
