import urls from '../const/form_urls';
import { HTTP, BaseService } from './base_service';

export default class FormService extends BaseService {
    async list () {
        try {
            const resp = await fetch(urls.FormList, this.payload);
            return await resp.json();
        } catch (error) {
            console.error('No se pudieron obtener los formularios');
            return [];
        }
    }

    async detail (id) {
        try {
            const resp = await fetch(
                urls.FormDetail(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error('No se pudo obtener el detalle del formulario');
            return [];
        }
    }

    async create (data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                urls.FormCreate,
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo crear el formulario');
            console.error(error);
            return {};
        }
    }

    async update (id, data) {
        try {
            this.setPayload(HTTP.PUT, JSON.stringify(data));
            const resp = await fetch(
                urls.FormUpdate(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo actualizar el formulario');
            console.error(error);
            return {};
        }
    }

    async delete (id) {
        try {
            this.setPayload(HTTP.DELETE);
            const resp = await fetch(
                urls.FormDelete(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo eliminar el formulario');
            console.error(error);
            return {};
        }
    }

    async show (id) {
        try {
            this.setPayload(HTTP.PUT);
            const resp = await fetch(
                urls.FormShow(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo desocultar el formulario');
            console.error(error);
            return {};
        }
    }

    async hide (id) {
        try {
            this.setPayload(HTTP.PUT);
            const resp = await fetch(
                urls.FormHide(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo ocultar el formulario');
            console.error(error);
            return {};
        }
    }
}
