import urls from '@/api_urls/supervisor/outbound_route_urls';
import { HTTP, BaseService } from './../base_service';

export default class OutboundRouteService extends BaseService {
    constructor () {
        super(urls, 'Ruta Saliente');
    }

    async sipTrunks () {
        try {
            const resp = await fetch(urls.OutboundRouteSipTrunks, this.payload);
            return await resp.json();
        } catch (error) {
            console.error('No se pudieron obtener las troncales sip');
            return [];
        }
    }

    async orphanTrunks (id) {
        try {
            const resp = await fetch(
                urls.OutboundRouteOrphanTrunks(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error('No se pudieron obtener las troncales huerfanas de la ruta saliente');
            return [];
        }
    }

    async reorder (data) {
        try {
            this.setPayload(HTTP.PUT, JSON.stringify(data));
            const resp = await fetch(
                urls.OutboundRouteReorder,
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo reordenar las rutas salientes');
            console.error(error);
            return {};
        }
    }
}
