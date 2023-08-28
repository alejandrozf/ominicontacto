import { WHATSAPP_EVENTS, WHATSAPP_MESSAGE, notificationEvent } from '@/globals/agent/whatsapp';
import STORE from '@/store';

export class WhatsappConsumer {
    constructor () {
        this.consumer = new WebSocket(
            `wss://${window.location.host}/channels/agent-console-whatsapp`
        );
        this.setConsumerEvents();
    }

    setConsumerEvents () {
        this.consumer.onopen = () => {
            console.log('Whatsapp Consumer OPEN: Conexión establecida');
        };

        this.consumer.onclose = (event) => {
            if (event.wasClean) {
                console.log(
                    'Whatsapp Consumer CLOSE: Conexión cerrada limpiamente'
                );
            } else {
                console.error('Whatsapp Consumer CLOSE: La conexión se cayó');
                console.error(event);
            }
        };

        this.consumer.onmessage = (event) => {
            const { type, args } = JSON.parse(event.data);
            if (type === WHATSAPP_EVENTS.NEW_MESSAGE) {
                this.handleNewMessageEvent(args);
            } else if (type === WHATSAPP_EVENTS.MESSAGE_STATUS) {
                this.handleMessageStatusEvent(args);
            } else if (type === WHATSAPP_EVENTS.NEW_CHAT) {
                this.handleNewChatEvent(args);
            } else if (type === WHATSAPP_EVENTS.CHAT_ATTENDED) {
                this.handleChatAttendedEvent(args);
            } else if (type === WHATSAPP_EVENTS.CHAT_TRANSFERED) {
                this.handleChatTransferedEvent(args);
            } else if (type === WHATSAPP_EVENTS.CHAT_EXPIRED) {
                this.handleChatExpiredEvent(args);
            }
        };

        this.consumer.onerror = (error) => {
            console.error('Whatsapp Consumer ERROR: ');
            console.error(error);
        };
    }

    handleNewMessageEvent (data = null) {
        console.log('Whatsapp Consumer NEW_MESSAGE: ');
        console.log(data);
        if (data) {
            STORE.dispatch('agtWhatsCoversationReciveMessage', {
                id: data.message_id,
                from: data.user,
                conversationId: data.chat_id,
                itsMine: data.sender === WHATSAPP_MESSAGE.SENDERS.AGENT,
                message: data.content,
                status: data.status,
                date: new Date(data.date)
            });
        }
    }

    handleMessageStatusEvent (data) {
        console.log('Whatsapp Consumer MESSAGE_STATUS: ');
        console.log(data);
    }

    handleNewChatEvent (data) {
        console.log('Whatsapp Consumer NEW_CHAT: ');
        console.log(data);
        STORE.dispatch('agtWhatsReceiveNewChat', data);
    }

    handleChatAttendedEvent (data) {
        console.log('Whatsapp Consumer CHAT_ATTENDED: ');
        console.log(data);
        notificationEvent(
            'WHATSAPP_CHAT_ATTENDED',
            `El chat de la campana (${data.campaign_name}), se atendio`,
            'INFO'
        );
    }

    handleChatTransferedEvent (data) {
        console.log('Whatsapp Consumer CHAT_TRANSFERED: ');
        console.log(data);
        notificationEvent(
            'WHATSAPP_CHAT_TRANSFERED',
            `El chat del cliente (${data.chat_info.client_name}), se te transfirio`,
            'INFO'
        );
    }

    handleChatExpiredEvent (data) {
        console.log('Whatsapp Consumer CHAT_EXPIRED: ');
        console.log(data);
        notificationEvent(
            'WHATSAPP_CHAT_EXPIRED',
            'El chat expiro debido a inactividad del agent/cliente',
            'WARNING'
        );
    }

    close () {
        this.consumer.close();
        this.consumer = null;
    }
}
