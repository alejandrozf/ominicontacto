import { WHATSAPP_EVENTS, WHATSAPP_MESSAGE } from '@/globals/agent/whatsapp';
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

    close () {
        this.consumer.close();
        this.consumer = null;
    }
}
