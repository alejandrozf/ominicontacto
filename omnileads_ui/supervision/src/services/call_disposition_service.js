import urls from '../const/call_disposition_urls';
import { HTTP, BaseService } from './apiBaseService';

export default class CallDispositionService extends BaseService {
    async list () {
        try {
            const resp = await fetch(urls.CallDispositionsList, this.payload);
            return await resp.json();
        } catch (error) {
            console.error('No se pudieron obtener las calificaciones');
            return [];
        }
    }

    async delete (id) {
        try {
            this.setPayload(HTTP.DELETE);
            const resp = await fetch(
                urls.CallDispositionsDelete(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo eliminar la calificacion');
            return [];
        }
    }

    async create (data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                urls.CallDispositionsCreate,
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo crear la calificacion');
            console.error(error);
            return {};
        }
    }

    async update (id, data) {
        try {
            this.setPayload(HTTP.PUT, JSON.stringify(data));
            const resp = await fetch(
                urls.CallDispositionsUpdate(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo actualizar la calificacion');
            console.error(error);
            return {};
        }
    }
}
