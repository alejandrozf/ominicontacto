import urls from '../const/external_site_urls';
import { HTTP, BaseService } from './base_service';

export default class ExternalSiteService extends BaseService {
    async list () {
        try {
            const resp = await fetch(urls.ExternalSitesList, this.payload);
            return await resp.json();
        } catch (error) {
            console.error('No se pudieron obtener los sitios externos');
            return [];
        }
    }

    async detail (id) {
        try {
            const resp = await fetch(
                urls.ExternalSitesDetail(id), this.payload);
            return await resp.json();
        } catch (error) {
            console.error('No se pudo obtener el detalle del sitio externo');
            return [];
        }
    }

    async hide (id) {
        try {
            this.setPayload(HTTP.PUT);
            const resp = await fetch(
                urls.ExternalSitesHide(id), this.payload);
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo ocultar el sitio externo');
            return [];
        }
    }

    async show (id) {
        try {
            this.setPayload(HTTP.PUT);
            const resp = await fetch(
                urls.ExternalSitesShow(id), this.payload);
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo desocultar el sitio externo');
            return [];
        }
    }

    async delete (id) {
        try {
            this.setPayload(HTTP.DELETE);
            const resp = await fetch(
                urls.ExternalSitesDelete(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo eliminar el sitio externo');
            return [];
        }
    }

    async create (data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                urls.ExternalSitesCreate,
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo crear el sitio externo');
            console.error(error);
            return {};
        }
    }

    async update (id, data) {
        try {
            this.setPayload(HTTP.PUT, JSON.stringify(data));
            const resp = await fetch(
                urls.ExternalSitesUpdate(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo actualizar el sitio externo');
            console.error(error);
            return {};
        }
    }
}
