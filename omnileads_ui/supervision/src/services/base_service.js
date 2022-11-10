import Cookies from 'universal-cookie';

export const HTTP = {
    POST: 'POST',
    GET: 'GET',
    PUT: 'PUT',
    DELETE: 'DELETE'
};

export const HEADER_TYPES = {
    JSON: 'application/json',
    FORM_DATA: 'multipart/form-data'
};

export class BaseService {
    constructor (urls, model) {
        this.urls = urls;
        this.model = model;
        this.cookies = new Cookies();
        this.formData = null;
        this.headers = {
            'X-CSRFToken': this.cookies.get('csrftoken'),
            'Content-Type': HEADER_TYPES.JSON
        };
        this.initPayload();
    }

    setPayload (method = HTTP.POST, body = null) {
        if (body) {
            this.payload.body = body;
        }
        this.payload.method = method;
    }

    initPayload () {
        this.payload = {
            method: HTTP.GET,
            credentials: 'same-origin',
            headers: this.headers
        };
    }

    async list () {
        try {
            const resp = await fetch(this.urls.List, this.payload);
            return await resp.json();
        } catch (error) {
            console.error(`Error al listar < ${this.model} >`);
            return [];
        } finally {
            this.initPayload();
        }
    }

    async create (data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                this.urls.Create,
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al crear < ${this.model} >`);
            return {};
        } finally {
            this.initPayload();
        }
    }

    async update (id, data) {
        try {
            this.setPayload(HTTP.PUT, JSON.stringify(data));
            const resp = await fetch(
                this.urls.Update(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al actualizar < ${this.model} >`);
            console.error(error);
            return {};
        } finally {
            this.initPayload();
        }
    }

    async detail (id) {
        try {
            const resp = await fetch(
                this.urls.Detail(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener detalle < ${this.model} >`);
            return [];
        } finally {
            this.initPayload();
        }
    }

    async delete (id) {
        try {
            this.setPayload(HTTP.DELETE);
            const resp = await fetch(
                this.urls.Delete(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al eliminar < ${this.model} >`);
            console.error(error);
            return {};
        } finally {
            this.initPayload();
        }
    }
}
