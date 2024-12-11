import urls from '@/api_urls/supervisor/external_site_authentication_urls';
import { HTTP, BaseService } from './../base_service';

export default class ExternalSiteAuthenticationService extends BaseService {
    constructor () {
        super(urls, 'Autenticacion de Sitio Externo');
    }

    async test (data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(urls.Test, this.payload);
            return await resp.json();
        } catch (error) {
            console.error(error);
            return {};
        }
    }
}
