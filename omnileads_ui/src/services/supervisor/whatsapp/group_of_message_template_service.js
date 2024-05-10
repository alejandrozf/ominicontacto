import urls from '@/api_urls/supervisor/whatsapp/group_of_message_template_urls';
import { BaseService } from '@/services/base_service';

export default class GroupOfMessageTemplateService extends BaseService {
    constructor () {
        super(urls, 'Grupo de plantillas de mensaje');
    }
}
