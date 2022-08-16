import urls from '../const/inbound_route_urls';
import { BaseService } from './base_service';

export default class InboundRouteService extends BaseService {
    constructor () {
        super(urls, 'Ruta Entrante');
    }

    async destinations () {
        try {
            const resp = await fetch(urls.InboundRouteDestinationsByType, this.payload);
            return await resp.json();
        } catch (error) {
            console.error('No se pudieron obtener los destinos');
            return [];
        }
    }
}
