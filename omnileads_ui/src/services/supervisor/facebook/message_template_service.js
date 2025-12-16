import urls from '@/api_urls/supervisor/facebook/message_template_urls';
import { BaseService } from '@/services/base_service';

export default class MessageTemplateService extends BaseService {
    constructor () {
        console.log('MessageTemplateService URLs >>>', urls);
        super(urls, 'Plantillas de Mensaje');
    }
}
