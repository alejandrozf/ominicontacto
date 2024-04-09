import urls from '@/api_urls/supervisor/whatsapp/provider_urls';
import { BaseService } from '@/services/base_service';

export default class ProviderService extends BaseService {
    constructor () {
        super(urls, 'Proveedor WhatsApp');
    }
}
