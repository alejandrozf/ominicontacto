/* eslint-disable no-unused-vars */
import Service from '@/services/agent/whatsapp/conversation_service';
import { HTTP_STATUS } from '@/globals';
import { WHATSAPP_MESSAGE } from '@/globals/agent/whatsapp';
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
        { conversationId, message }
    ) {
        try {
            const { status, data } = await service.sendTextMessage(
                conversationId,
                { content: message.message }
            );
            if (status === HTTP_STATUS.SUCCESS) {
                commit('agtWhatsCoversationSendMessage', message);
            }
        } catch (error) {
            console.error('===> ERROR al enviar mensaje de texto');
            console.error(error);
        }
    },
    agtWhatsCoversationReciveMessage (
        { commit },
        message
    ) {
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
            if (status === HTTP_STATUS.SUCCESS) {
                commit(
                    'agtWhatsConversationInitMessages',
                    data.messages.map((msg) => {
                        return {
                            id: msg.id,
                            from: msg.user,
                            conversationId: msg.conversation,
                            itsMine: msg.sender === WHATSAPP_MESSAGE.SENDERS.AGENT,
                            message: msg.content,
                            status: msg.status,
                            date: new Date(msg.date)
                        };
                    })
                );
            }
        } catch (error) {
            console.error('===> ERROR al obtener mensajes de la conversacion');
            console.error(error);
        }
    }
};
