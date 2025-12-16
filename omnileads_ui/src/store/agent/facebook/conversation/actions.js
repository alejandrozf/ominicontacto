/* eslint-disable */
import Service from '@/services/agent/facebook/conversation_service';
import { HTTP_STATUS } from '@/globals';
import { resetStoreDataByAction } from '@/utils';
const service = new Service();

const getMessageInfo = ({ $t, data = null, itsMine = true }) => {
    const senderName = data && data.sender && data.sender.name ? data.sender.name : null;
    const senderPhone = data && data.sender && data.sender.phone ? data.sender.phone : $t('globals.whatsapp.automatic_agent');
    var clientName = "-"
    if (data && data.contact_data) {
        if (data.contact_data.nombre)
            clientName = data.contact_data.nombre;
        else if (data.contact_data.name)
            clientName = data.contact_data.name;
    }
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
        file: data && data.file ? data.file : null
    };
};

export default {
    async agtFacebookConversationSendAttachmentMessage(
        { commit },
        { conversationId = null, formData, pageId = null, messages, $t}
    ) {
        try {
            console.log('Sending attachment message with formData:', formData);
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
                const itsMine = data.origin === pageId;
                const message = getMessageInfo({ $t, data, itsMine });
                messages.push(message);
                await commit('agtFacebookConversationSendMessage', message);
            }
            await resetStoreDataByAction({
                action: 'agtFacebookSetConversationMessages',
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
    async agtFacebookConversationSendTextMessage (
        { commit },
        { conversationId = null, message = null, pageId = null, $t }
    ) {
        try {
            if (!conversationId || !message || !pageId) {
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
            console.log('>>> Text message send response:', response);
            const { status, data } = response;
            if (status === HTTP_STATUS.SUCCESS) {
                const itsMine = data.origin === pageId;
                const message = getMessageInfo({ $t, data, itsMine });
                console.log('Committing sent message:', message);
                await commit('agtFacebookConversationSendMessage', message);
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
    async agtFacebookConversationSendTemplateMessage(
        { commit, state },
        { conversationId = null, templateId = null, pageId = null, $t }
    ) {
        try {
            if (!conversationId || !templateId || !pageId) {
                return { status: HTTP_STATUS.ERROR, message: 'Error al enviar template de Texto' };
            }
            const result = await service.sendTemplateMessage(conversationId, { template_id: templateId });
            console.log('>>> Template message send response:', result);

            const { status, data } = result;
            if (status === HTTP_STATUS.SUCCESS) {
                const itsMine = data.origin === pageId;
                const message = getMessageInfo({ $t, data, itsMine });

                // // Creamos un nuevo array para reemplazar la referencia
                // const updatedMessages = [...this.agtFacebookConversationMessages, message];
                // // Guardamos en store
                // await resetStoreDataByAction({
                //     action: 'agtFacebookSetConversationMessages',
                //     data: updatedMessages
                // });

                await commit('agtFacebookConversationSendMessage', message);
            }

            return result;
        } catch (error) {
            console.error('===> ERROR al enviar template de texto', error);
            return { status: HTTP_STATUS.ERROR, message: 'Error al enviar template de Texto' };
        }
    },
    async agtFacebookConversationReactiveExpiredConversation(
        { commit },
        { conversationId = null, templateId = null, params_header, params, pageId, messages, $t }
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
                { template_id: templateId, params_header, params }
            );
            const { status, data } = result;
            if (status === HTTP_STATUS.SUCCESS) {
                const itsMine = data.origin === pageId;
                const message = getMessageInfo({ $t, data, itsMine });
                messages.push(message);
            }
            await resetStoreDataByAction({
                action: 'agtFacebookSetConversationMessages',
                data: messages
            });
            await resetStoreDataByAction({
                action: 'agtFacebookConversationDetailInit',
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
    agtFacebookConversationReciveMessage ({ commit }, message) {
        try {
            commit('agtFacebookConversationReciveMessage', message);
        } catch (error) {
            console.error('===> ERROR al recibir mensaje de texto');
            console.error(error);
        }
    },
    async agtFacebookConversationDetail ({ commit }, { conversationId = null, $t }) {
        try {
            if (!conversationId) {
                commit('agtFacebookConversationInitMessages', []);
                commit('agtFacebookConversationInfoInit', {});
                return {
                    status: HTTP_STATUS.ERROR,
                    message: 'Error al obtener detalle de la conversacion'
                };
            }
            console.log('Fetching conversation detail for ID:', conversationId);
            const { status, data } = await service.getConversationDetail(
                conversationId
            );
            console.log('Received data:', data);
            if (status === HTTP_STATUS.SUCCESS) {
                commit(
                    'agtFacebookConversationInitMessages',
                    data.messages.map((msg) => {
                        const itsMine = msg.origin === data.page.page_id;
                        return getMessageInfo({ $t, data: msg, itsMine });
                    })
                );
                console.log('Committed messages:', data.messages);
                commit('agtFacebookConversationInfoInit', data);
            }
        } catch (error) {
            console.error('===> ERROR al obtener detalle de la conversacion');
            console.error(error);
            commit('agtFacebookConversationInitMessages', []);
            commit('agtFacebookConversationInfoInit', {});
            return {
                status: HTTP_STATUS.ERROR,
                message: 'Error al obtener detalle de la conversacion'
            };
        }
    },
    async agtFacebookChatsListInit ({ commit }) {
        try {
            const { status, data } = await service.getAgentChatsList();
            commit('agtFacebookChatsListInit', {
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
            commit('agtFacebookChatsListInit', { isNew: [], inProgress: [] });
        }
    },
    agtFacebookReceiveNewChat ({ commit }, chat = null) {
        try {
            commit('agtFacebookReceiveNewChat', chat);
        } catch (error) {
            console.error('===> ERROR al recibir nuevo chat');
            console.error(error);
            commit('agtFacebookReceiveNewChat', null);
        }
    },
    async agtFacebookCoversationRequest ({ commit }, conversationId = null) {
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
    agtFacebookSetConversationMessages ({ commit }, messages = []) {
        try {
            commit('agtFacebookConversationInitMessages', messages);
        } catch (error) {
            console.error('===> ERROR al settear Mensajes de la conversacion');
            console.error(error);
            commit('agtFacebookConversationInitMessages', []);
        }
    },
    agtFacebookSetConversationInfo ({ commit }, info = null) {
        try {
            commit('agtFacebookSetConversationInfo', info);
        } catch (error) {
            console.error('===> ERROR al settear info de la conversacion');
            console.error(error);
            commit('agtFacebookSetConversationInfo', null);
        }
    },
    agtFacebookRestartExpiredCoversation ({ commit }, info = null) {
        try {
            commit('agtFacebookRestartExpiredCoversation', info);
        } catch (error) {
            console.error(
                '===> ERROR al actualizar la fecha de expiracion de la conversacion'
            );
            console.error(error);
            commit('agtFacebookRestartExpiredCoversation', null);
        }
    },
    async agtFacebookInitNewConversation ({ commit }, data) {
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
    },
    async agtFacebookMarkMessageAsRead ({ commit }, data) {
        try {
            return await service.markMessageAsRead(data);
        } catch (error) {
            console.error('===> ERROR al marcar msg como leido');
            console.error(error);
            return {
                status: HTTP_STATUS.ERROR,
                message: 'ERROR al marcar msg como leido'
            };
        }
    }
};
