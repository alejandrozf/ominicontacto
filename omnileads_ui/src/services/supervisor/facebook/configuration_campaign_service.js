import urls from '@/api_urls/supervisor/whatsapp/configuration_campaign_urls';
import { BaseService } from '@/services/base_service';

export default class WhatsappConfigurationCampaignService extends BaseService {
    constructor () {
        super(urls, 'Whatsapp Configuracion Campaign');
    }
}
