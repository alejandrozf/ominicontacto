import urls from '../const/external_system_urls';
import { HTTP, BaseService } from './base_service';

export default class ExternalSystemService extends BaseService {
    async list () {
        try {
            const resp = await fetch(urls.ExternalSystemsList, this.payload);
            return await resp.json();
        } catch (error) {
            console.error('No se pudieron obtener los sistemas externos');
            return [];
        }
    }

    async detail (id) {
        try {
            const resp = await fetch(
                urls.ExternalSystemsDetail(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error('No se pudo obtener el detalle del sistema externo');
            return [];
        }
    }

    async create (data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                urls.ExternalSystemsCreate,
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo crear el sistema externo');
            console.error(error);
            return {};
        }
    }

    async update (id, data) {
        try {
            this.setPayload(HTTP.PUT, JSON.stringify(data));
            const resp = await fetch(
                urls.ExternalSystemsUpdate(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo actualizar el sistema externo');
            console.error(error);
            return {};
        }
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
