/* eslint-disable no-unused-vars */
import Service from '@/services/agent/whatsapp/conversation_service';
import { HTTP_STATUS } from '@/globals';
const service = new Service();

export default {
    async agtWhatsCoversationSendAttachmentMessage (
        { commit },
        { conversationId, message }
    ) {
        try {
            const { status, data } = await service.sendAttachmentMessage(
                conversationId,
                message
            );
            if (status === HTTP_STATUS.SUCCESS) {
                await commit('agtWhatsCoversationSendMessage', message);
            }
        } catch (error) {
            console.error('===> ERROR al enviar mensaje multimedia');
            console.error(error);
        }
    },
    async agtWhatsCoversationSendTextMessage (
        { commit },
        { conversationId, message, phoneLine }
    ) {
        try {
            const { status, data } = await service.sendTextMessage(
                conversationId,
                { message: message.message, destination: message.destination }
            );
            if (status === HTTP_STATUS.SUCCESS) {
                const itsMine = data.origen === phoneLine;
                const message = {
                    id: data.id,
                    from: itsMine
                        ? `Agente (${data.sender.name})`
                        : data.sender.name,
                    conversationId: data.conversation,
                    itsMine,
                    message: data.content.text,
                    status: data.status || null,
                    date: new Date(data.timestamp)
                };
                await commit('agtWhatsCoversationSendMessage', message);
            }
        } catch (error) {
            console.error('===> ERROR al enviar mensaje de texto');
            console.error(error);
        }
    },
    async agtWhatsCoversationSendTemplateMessage (
        { commit },
        { conversationId, templateId, phoneLine, messages }
    ) {
        try {
            console.log('===> Messages Antes');
            console.log(messages);
            const result = await service.sendTemplateMessage(
                conversationId,
                { template_id: templateId }
            );
            const { status, data } = result;
            if (status === HTTP_STATUS.SUCCESS) {
                const itsMine = data.origen === phoneLine;
                const message = {
                    id: data.id,
                    from: itsMine
                        ? `Agente (${data.sender.name})`
                        : data.sender.name,
                    conversationId: data.conversation,
                    itsMine,
                    message: data.content.text,
                    status: data.status || null,
                    date: new Date(data.timestamp)
                };
                messages.push(message);
                console.log('===> Messages Despues');
                console.log(messages);
            }
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
        { conversationId, templateId, params, phoneLine }
    ) {
        try {
            const result = await service.sendWhatsappTemplateMessage(
                conversationId,
                { template_id: templateId, params }
            );
            const { status, data } = result;
            if (status === HTTP_STATUS.SUCCESS) {
                const itsMine = data.origen === phoneLine;
                const message = {
                    id: data.id,
                    from: itsMine
                        ? `Agente (${data.sender.name})`
                        : data.sender.name,
                    conversationId: data.conversation,
                    itsMine,
                    message: data.content.text,
                    status: data.status || null,
                    date: new Date(data.timestamp)
                };
                await commit('agtWhatsCoversationSendMessage', message);
            }
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
    agtWhatsCoversationReciveMessage ({ commit }, message) {
        try {
            commit('agtWhatsCoversationReciveMessage', message);
        } catch (error) {
            console.error('===> ERROR al recibir mensaje de texto');
            console.error(error);
        }
    },
    async agtWhatsConversationDetail ({ commit }, chatId) {
        try {
            const { status, data } = await service.getConversationDetail(
                chatId
            );
            if (status === HTTP_STATUS.SUCCESS) {
                commit(
                    'agtWhatsConversationInitMessages',
                    data.messages.map((msg) => {
                        const itsMine = msg.origen === data.line_number;
                        return {
                            id: msg.id,
                            from: itsMine
                                ? `Agente (${msg.sender.name})`
                                : msg.sender.name,
                            conversationId: msg.conversation,
                            itsMine,
                            message: msg.content.text,
                            status: msg.status || null,
                            date: new Date(msg.timestamp)
                        };
                    })
                );
                commit('agtWhatsConversationInfoInit', data);
            }
        } catch (error) {
            console.error('===> ERROR al obtener detalle de la conversacion');
            console.error(error);
            commit('agtWhatsConversationInitMessages', []);
            commit('agtWhatsConversationInfoInit', {});
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
    async agtWhatsReceiveNewChat ({ commit }, chat) {
        try {
            commit('agtWhatsReceiveNewChat', chat);
        } catch (error) {
            console.error('===> ERROR al recibir nuevo chat');
            console.error(error);
            commit('agtWhatsReceiveNewChat', null);
        }
    },
    async agtWhatsCoversationRequest ({ commit }, conversationId) {
        try {
            return await service.requestConversation({
                id: conversationId
            });
        } catch (error) {
            console.error('===> ERROR al pedir una conversacion');
            console.error(error);
        }
    },
    async agtWhatsSetCoversationId ({ commit }, conversationId) {
        try {
            commit('agtWhatsSetCoversationId', conversationId);
        } catch (error) {
            console.error('===> ERROR al settear ID de la conversacion');
            console.error(error);
            commit('agtWhatsSetCoversationId', null);
        }
    },
    async agtWhatsSetCoversationMessages ({ commit }, messages = []) {
        try {
            commit('agtWhatsConversationInitMessages', messages);
        } catch (error) {
            console.error('===> ERROR al settear Mensajes de la conversacion');
            console.error(error);
            commit('agtWhatsConversationInitMessages', []);
        }
    },
    async agtWhatsSetCoversationCampaignId ({ commit }, campaignId = null) {
        try {
            commit('agtWhatsSetCoversationCampaignId', campaignId);
        } catch (error) {
            console.error('===> ERROR al settear campaignId de la conversacion');
            console.error(error);
            commit('agtWhatsSetCoversationCampaignId', null);
        }
    }
};
