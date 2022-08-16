import urls from '../const/pause_urls';
import { HTTP, BaseService } from './base_service';

export default class PauseService extends BaseService {
    constructor () {
        super(urls, 'Pausa');
    }

    async reactivate (id) {
        try {
            this.setPayload(HTTP.PUT);
            const resp = await fetch(
                urls.Reactivate(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error('Error al reactivar < Pausa >');
            console.error(error);
            return {};
        } finally {
            this.initPayload();
        }
    }
}
