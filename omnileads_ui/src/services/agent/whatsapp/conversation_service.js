import urls from '@/api_urls/supervisor/whatsapp/line_urls';
import { BaseService } from '@/services/base_service';

export default class WhatsappConversationService extends BaseService {
    constructor () {
        super(urls, 'Whatsapp <Conversation>');
    }

    getMessagesByConversationId (id) {
        try {
            // const resp = await fetch(this.urls.Campaigns, this.payload);
            // return await resp.json();
            return [
                {
                    id: 1,
                    from: 'Agente',
                    itsMine: true,
                    message: 'Lorem ipsum dolor sit amet consectetur, adipisicing elit',
                    date: new Date()
                },
                {
                    id: 2,
                    from: '134134134',
                    itsMine: false,
                    message:
                        'Lorem ipsum dolor sit amet consectetur, adipisicing elit. Quo consectetur veniam exercitationem, quia adipisci aperiam voluptate maiores quibusdam, tempore aspernatur in unde illum aliquid saepe nesciunt cupiditate, est quaerat et?',
                    date: new Date()
                },
                {
                    id: 3,
                    from: 'Agente',
                    itsMine: true,
                    message: 'Lorem ipsum dolor sit amet consectetur, adipisicing elit',
                    date: new Date()
                },
                {
                    id: 4,
                    from: '134134134',
                    itsMine: false,
                    message: 'Lorem ipsum dolor sit amet consectetur',
                    date: new Date()
                },
                {
                    id: 5,
                    from: 'Agente',
                    itsMine: true,
                    message:
                        'Lorem ipsum dolor sit amet consectetur, adipisicing elit asdf asdf asdf asdf',
                    date: new Date()
                },
                {
                    id: 6,
                    from: '134134134',
                    itsMine: false,
                    message:
                        'Lorem ipsum dolor sit amet consectetur, adipisicing elit. tempore aspernatur in unde illum aliquid saepe nesciunt cupiditate, est quaerat et?',
                    date: new Date()
                }
            ];
        } catch (error) {
            console.error(`Error al obtener < Mensajes de la Conversacion >`);
            return [];
        } finally {
            this.initPayload();
        }
    }
}
