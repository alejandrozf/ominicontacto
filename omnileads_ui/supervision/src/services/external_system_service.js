import urls from '../const/external_system_urls';
import { BaseService } from './base_service';

export default class ExternalSystemService extends BaseService {
    constructor () {
        super(urls, 'Sistema Externo');
    }

    async getAgents () {
        try {
            const resp = await fetch(urls.AgentsExternalSystemList, this.payload);
            return await resp.json();
        } catch (error) {
            console.error('Error al obtener agentes');
            console.error(error);
            return {};
        }
    }
}
