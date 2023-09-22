/* eslint-disable no-unused-vars */
import Service from '@/services/agent/whatsapp/conversation_service';
import { HTTP_STATUS } from '@/globals';
// import { WHATSAPP_MESSAGE } from '@/globals/agent/whatsapp';
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
                commit('agtWhatsCoversationSendMessage', message);
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
                    message: data.content[`${data.type}`],
                    status: data.status || null,
                    date: new Date(data.timestamp)
                };
                commit('agtWhatsCoversationSendMessage', message);
            }
        } catch (error) {
            console.error('===> ERROR al enviar mensaje de texto');
            console.error(error);
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
    async agtWhatsConversationInitMessages ({ commit }, chatId) {
        try {
            const { status, data } = await service.getMessagesByConversationId(
                chatId
            );
            console.log('===> Conversation Messages');
            console.log(data);
            if (status === HTTP_STATUS.SUCCESS) {
                commit(
                    'agtWhatsConversationInitMessages',
                    data.messages.map((msg) => {
                        const itsMine = msg.origen === '5493764962109';
                        return {
                            id: msg.id,
                            from: itsMine
                                ? `Agente (${msg.sender.name})`
                                : msg.sender.name,
                            conversationId: msg.conversation,
                            itsMine,
                            message: msg.content[`${msg.type}`],
                            status: msg.status || null,
                            date: new Date(msg.timestamp)
                        };
                    })
                );
                // commit('agtWhatsConversationInfoInit', data.conversation_info);
            }
        } catch (error) {
            console.error('===> ERROR al obtener mensajes de la conversacion');
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
                            message: msg.content[`${msg.type}`],
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
    }
};
