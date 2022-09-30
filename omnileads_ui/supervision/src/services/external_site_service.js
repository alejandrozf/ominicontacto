import urls from '../const/external_site_urls';
import { HTTP, BaseService } from './base_service';

export default class ExternalSiteService extends BaseService {
    constructor () {
        super(urls, 'Sitio Externo');
    }

    async hide (id) {
        try {
            this.setPayload(HTTP.PUT);
            const resp = await fetch(
                urls.Hide(id), this.payload);
            return await resp.json();
        } catch (error) {
            console.error('Error al ocultar el < Sitio Externo >');
            return [];
        } finally {
            this.initPayload();
        }
    }

    async show (id) {
        try {
            this.setPayload(HTTP.PUT);
            const resp = await fetch(
                urls.Show(id), this.payload);
            return await resp.json();
        } catch (error) {
            console.error('Error al desocultar el < Sitio Externo >');
            return [];
        } finally {
            this.initPayload();
        }
    }
}
