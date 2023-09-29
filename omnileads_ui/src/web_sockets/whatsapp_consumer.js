import {
    WHATSAPP_EVENTS,
    notificationEvent,
    NOTIFICATION
} from '@/globals/agent/whatsapp';
import STORE from '@/store';
const MAX_RECONNECT_ATTEMPTS = 5;

export class WhatsappConsumer {
    constructor () {
        this.reconnectIntent = 0;
        this.openSocket();
    }

    setConsumerEvents () {
        if (this.consumer) {
            this.consumer.onopen = () => {
                console.log('Whatsapp Consumer OPEN: Conexión establecida');
            };

            this.consumer.onclose = (event) => {
                this.close();
                if (event.wasClean) {
                    console.log(
                        'Whatsapp Consumer CLOSE: Conexión cerrada limpiamente'
                    );
                } else {
                    console.error(
                        'Whatsapp Consumer CLOSE: La conexión se cayó'
                    );
                    console.error(event);
                    if (this.reconnectIntent < MAX_RECONNECT_ATTEMPTS) {
                        this.reconnectIntent++;
                        setTimeout(() => {
                            this.openSocket();
                        }, 3000);
                    } else {
                        this.close();
                    }
                }
            };

            this.consumer.onmessage = (event) => {
                const { type, args } = JSON.parse(event.data);
                console.log('Whatsapp Consumer MESSAGE');
                console.log(event.data);
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
    }

    openSocket () {
        if (!this.consumer || this.consumer.readyState === WebSocket.CLOSED) {
            this.consumer =
                new WebSocket(
                    `wss://${window.location.host}/channels/agent-console-whatsapp`
                ) || null;
            if (this.consumer) {
                this.setConsumerEvents();
            } else {
                console.error(
                    'Whatsapp Consumer: No se pudo establecer la conexión'
                );
                if (this.reconnectIntent < MAX_RECONNECT_ATTEMPTS) {
                    this.reconnectIntent++;
                    setTimeout(() => {
                        this.openSocket();
                    }, 3000);
                } else {
                    this.close();
                }
            }
        } else {
            console.log('Whatsapp Consumer: Ya existe una conexión abierta');
        }
    }

    handleNewMessageEvent (data = null) {
        console.log('Whatsapp Consumer NEW_MESSAGE: ');
        console.log(data);
        if (data) {
            const itsMine = data.origen === '5493764962109';
            STORE.dispatch('agtWhatsCoversationReciveMessage', {
                id: data.message_id,
                from: itsMine
                    ? `Agente (${data.sender.name})`
                    : data.sender.name || data.sender.phone,
                conversationId: data.chat_id,
                itsMine,
                message: data.content.text,
                status: data.status || null,
                date: new Date(data.timestamp)
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
            NOTIFICATION.TITLES.WHATSAPP_CHAT_ATTENDED,
            `El chat de la campana (${data.campaign_name}), se atendio`,
            NOTIFICATION.ICONS.INFO
        );
    }

    handleChatTransferedEvent (data) {
        console.log('Whatsapp Consumer CHAT_TRANSFERED: ');
        console.log(data);
        notificationEvent(
            NOTIFICATION.TITLES.WHATSAPP_CHAT_TRANSFERED,
            `El chat del cliente (${data.chat_info.client_name}), se te transfirio`,
            NOTIFICATION.ICONS.INFO
        );
    }

    handleChatExpiredEvent (data) {
        console.log('Whatsapp Consumer CHAT_EXPIRED: ');
        console.log(data);
        notificationEvent(
            NOTIFICATION.TITLES.WHATSAPP_CHAT_EXPIRED,
            'El chat expiro debido a inactividad del agent/cliente',
            NOTIFICATION.ICONS.WARNING
        );
    }

    close () {
        if (this.consumer && this.consumer.readyState !== WebSocket.CLOSED) {
            this.consumer.close();
            this.consumer = null;
            if (this.reconnectIntent >= MAX_RECONNECT_ATTEMPTS) {
                console.warn('Whatsapp Consumer MAX_RECONNECT_ATTEMPTS');
            }
            console.log('Whatsapp Consumer CLOSE: Conexión cerrada');
        } else {
            console.log('No hay una conexión WebSocket activa para cerrar.');
        }
    }
}
