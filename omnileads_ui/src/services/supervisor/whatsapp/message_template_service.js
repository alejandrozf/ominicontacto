import urls from '@/api_urls/supervisor/whatsapp/message_template_urls';
import { BaseService } from '@/services/base_service';

export default class MessageTemplateService extends BaseService {
    constructor () {
        super(urls, 'Plantillas de Mensaje');
    }
}
