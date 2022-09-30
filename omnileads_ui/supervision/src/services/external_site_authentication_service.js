import urls from '../const/external_site_authentication_urls';
import { BaseService } from './base_service';

export default class ExternalSiteAuthenticationService extends BaseService {
    constructor () {
        super(urls, 'Autenticacion de Sitio Externo');
    }
}
