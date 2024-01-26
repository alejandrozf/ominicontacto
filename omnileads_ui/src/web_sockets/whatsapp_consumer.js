import {
    WHATSAPP_EVENTS,
    notificationEvent,
    NOTIFICATION
} from '@/globals/agent/whatsapp';
import STORE from '@/store';
import { fireNotification } from '@/helpers/sweet_alerts_helper';
const MAX_RECONNECT_ATTEMPTS = 5;
const TIME_TO_RETRY = 15; // Segs
const TIME_WAITING_CONNECTION = 5; // Segs

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
        url = `wss://${window.location.host}/channels/agent-console-whatsapp`
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

    setBaseSocketEvents () {
        return new Promise((resolve) => {
            try {
                if (this.consumer) {
                    this.consumer.onopen = () => {
                        console.log('Whatsapp Consumer OPEN: Connection established OK');
                    };
                    this.consumer.onclose = (event) => {
                        this.close();
                        if (event?.wasClean) {
                            console.log(
                                'Whatsapp Consumer CLOSE: Conection closed cleanly'
                            );
                        } else {
                            console.error(
                                `Whatsapp Consumer CLOSE: Conection closed uncleanly (code: ${event?.code}), trying connect again...`
                            );
                            console.error(event?.reason);
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
                    resolve(true);
                }
            } catch (error) {
                console.error('Whatsapp Consumer Error on set base socket events');
                console.error(error?.message);
                resolve(false);
            }
        });
    }

    open () {
        try {
            if (!this.consumer || this.consumer.readyState === WebSocket.CLOSED) {
                this.consumer = new WebSocket(this.url);
                console.log('Whatsapp Consumer: Waiting connection...');
                setTimeout(async () => {
                    if (this.consumer && this.consumer.readyState === WebSocket.OPEN) {
                        console.log('Whatsapp Consumer: Connection established OK');
                        await this.setBaseSocketEvents();
                    } else {
                        console.error(
                            'Whatsapp Consumer: Connection could not be established, trying again...'
                        );
                        this.handleReconnect();
                    }
                }, TIME_WAITING_CONNECTION * 1000);
            } else {
                console.log('Whatsapp Consumer: Already exists a connection, using it...');
            }
        } catch (error) {
            console.error('Whatsapp Consumer OPEN ERROR');
            console.error(error?.message);
            this.handleReconnect();
        }
    }

    close () {
        if (this.consumer && this.consumer.readyState !== WebSocket.CLOSED) {
            this.consumer.close();
            this.consumer = null;
            if (this.reconnectIntent >= MAX_RECONNECT_ATTEMPTS) {
                console.warn('Whatsapp Consumer MAX_RECONNECT_ATTEMPTS');
            }
            console.log('Whatsapp Consumer CLOSE: Connection closed');
        } else {
            console.log('Whatsapp Consumer CLOSE: Not exists a connection to close');
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

    async handleNewChatEvent (data = null) {
        await notificationEvent(
            NOTIFICATION.TITLES.WHATSAPP_NEW_CHAT,
            'Nueva conversacion en espera de ser atendida',
            NOTIFICATION.ICONS.INFO
        );
        if (data) STORE.dispatch('agtWhatsReceiveNewChat', data);
    }

    async handleChatAttendedEvent (data) {
        await notificationEvent(
            NOTIFICATION.TITLES.WHATSAPP_CHAT_ATTENDED,
            `El chat de la campana (${data.campaign_name}), se atendio`,
            NOTIFICATION.ICONS.INFO
        );
    }

    async handleChatTransferedEvent (data) {
        await notificationEvent(
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
