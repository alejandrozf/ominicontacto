import urls from '@/api_urls/supervisor/whatsapp/group_of_whatsapp_template_urls';
import { BaseService } from '@/services/base_service';

export default class GroupOfWhatsappTemplateService extends BaseService {
    constructor () {
        super(urls, 'Grupo de Whatsapp Templates');
    }
}
