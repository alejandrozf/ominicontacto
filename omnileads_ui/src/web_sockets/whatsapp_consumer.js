import {
    WHATSAPP_EVENTS,
    notificationEvent,
    NOTIFICATION
} from '@/globals/agent/whatsapp';
import STORE from '@/store';
import { fireNotification } from '@/helpers/sweet_alerts_helper';
const MAX_RECONNECT_ATTEMPTS = 5;
const TIME_TO_RETRY = 15; // Segs

export class WhatsappConsumer {
    static #instance = null;

    constructor (
        url = `wss://${window.location.host}/channels/agent-console-whatsapp`
    ) {
        this.url = url;
        this.reconnectIntent = 0;
        this.consumer = null;
        this.open();
    }

    static getInstance ({
        url = `wss://${window.location.host}/channels/agent-console-whatsapp`,
        $t = null
    }) {
        if (!WhatsappConsumer.#instance) {
            WhatsappConsumer.#instance = new WhatsappConsumer(url);
        }
        return WhatsappConsumer.#instance;
    }

    isConnected () {
        return this.consumer && this.consumer.readyState === WebSocket.OPEN;
    }

    async consumerCloseNotification () {
        await fireNotification({
            title: 'Error',
            text: 'Whatsapp Socket: Connection could not be established, please reload the page',
            icon: 'error',
            footer: 'If the problem persists, contact the administrator'
        });
    }

    setConsumerEvents () {
        if (this.consumer) {
            this.consumer.onopen = () => {
                console.log('Whatsapp Consumer OPEN: Conexión establecida');
            };
            this.consumer.onclose = (event) => {
                this.close();
                if (event?.wasClean) {
                    console.log(
                        'Whatsapp Consumer CLOSE: Conexión cerrada limpiamente'
                    );
                } else {
                    console.error(
                        'Whatsapp Consumer CLOSE: La conexión se cayó'
                    );
                    this.handleReconnect();
                }
            };

            this.consumer.onmessage = (event) => {
                const { type, args } = JSON.parse(event.data);
                this.handleEventByType(type, args);
            };

            this.consumer.onerror = (error) => {
                console.error('Whatsapp Consumer ERROR:');
                console.error(error);
            };
        }
    }

    open () {
        try {
            if (!this.consumer || this.consumer.readyState === WebSocket.CLOSED) {
                this.consumer = new WebSocket(this.url);
                if (this.consumer && this.consumer.readyState === WebSocket.OPEN) {
                    this.setConsumerEvents();
                } else {
                    console.error(
                        'Whatsapp Consumer: No se pudo establecer la conexión'
                    );
                    this.handleReconnect();
                }
            } else {
                console.log('Whatsapp Consumer: Ya existe una conexión abierta');
            }
        } catch (error) {
            console.error('Whatsapp Consumer OPEN ERROR');
            console.error(error?.message);
        }
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

    handleEventByType (type, args) {
        switch (type) {
        case WHATSAPP_EVENTS.NEW_MESSAGE:
            this.handleNewMessageEvent(args);
            break;
        case WHATSAPP_EVENTS.MESSAGE_STATUS:
            this.handleMessageStatusEvent(args);
            break;
        case WHATSAPP_EVENTS.NEW_CHAT:
            this.handleNewChatEvent(args);
            break;
        case WHATSAPP_EVENTS.CHAT_ATTENDED:
            this.handleChatAttendedEvent(args);
            break;
        case WHATSAPP_EVENTS.CHAT_TRANSFERED:
            this.handleChatTransferedEvent(args);
            break;
        case WHATSAPP_EVENTS.CHAT_EXPIRED:
            this.handleChatExpiredEvent(args);
            break;
        default:
            break;
        }
    }

    handleReconnect () {
        this.consumerCloseNotification();
        if (this.reconnectIntent < MAX_RECONNECT_ATTEMPTS) {
            this.reconnectIntent++;
            setTimeout(() => {
                this.open();
            }, TIME_TO_RETRY * 1000);
        } else {
            this.close();
        }
    }

    handleNewMessageEvent (data = null) {
        if (data) STORE.dispatch('agtWhatsCoversationReciveMessage', data);
    }

    handleMessageStatusEvent (data = null) {
        if (data) STORE.dispatch('agtWhatSendMessageStatus', data);
    }

    handleNewChatEvent (data = null) {
        notificationEvent(
            NOTIFICATION.TITLES.WHATSAPP_NEW_CHAT,
            'Nueva conversacion en espera de ser atendida',
            NOTIFICATION.ICONS.INFO
        );
        if (data) STORE.dispatch('agtWhatsReceiveNewChat', data);
    }

    handleChatAttendedEvent (data) {
        notificationEvent(
            NOTIFICATION.TITLES.WHATSAPP_CHAT_ATTENDED,
            `El chat de la campana (${data.campaign_name}), se atendio`,
            NOTIFICATION.ICONS.INFO
        );
    }

    handleChatTransferedEvent (data) {
        notificationEvent(
            NOTIFICATION.TITLES.WHATSAPP_CHAT_TRANSFERED,
            `El chat del cliente (${data.chat_info.client_name}), se te transfirio`,
            NOTIFICATION.ICONS.INFO
        );
    }

    async handleChatExpiredEvent (data = null) {
        await STORE.dispatch('agtWhatsRestartExpiredCoversation', {
            conversationId:
                data && data.conversation_id ? data.conversation_id : null,
            expire: data && data.expire ? data.expire : null
        });
        await notificationEvent(
            NOTIFICATION.TITLES.SUCCESS,
            'La conversacion se reactivo de forma exitosa',
            NOTIFICATION.ICONS.INFO
        );
    }
}
