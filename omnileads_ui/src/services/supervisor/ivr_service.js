import urls from '@/api_urls/supervisor/ivr_urls';
import { BaseService, HTTP } from './../base_service';

export default class IVRService extends BaseService {
    constructor () {
        super(urls, 'IVR');
    }

    async ivrAudios () {
        try {
            const resp = await fetch(this.urls.IVRAudioOptions, this.payload);
            return await resp.json();
        } catch (error) {
            console.error(`Error al listar los audios para IVR`);
            return [];
        } finally {
            this.initPayload();
        }
    }

    async ivrDestinations () {
        try {
            const resp = await fetch(this.urls.IVRDestinations, this.payload);
            return await resp.json();
        } catch (error) {
            console.error(`Error al listar los destinos para IVR`);
            return [];
        } finally {
            this.initPayload();
        }
    }

    async create (data) {
        try {
            this.formData = new FormData();
            for (const key in data) {
                if (['main_audio_ext',
                    'time_out_audio_ext',
                    'invalid_audio_ext'].includes(key) && data[key]) {
                    this.formData.set(`${key}`, data[key], data[key].name);
                } else {
                    this.formData.set(`${key}`, data[key]);
                }
            }
            this.formData.set('destination_options', JSON.stringify(data.destination_options));
            this.payload = {
                method: HTTP.POST,
                body: this.formData,
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': this.cookies.get('csrftoken')
                }
            };
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
            this.formData = new FormData();
            for (const key in data) {
                if (['main_audio_ext',
                    'time_out_audio_ext',
                    'invalid_audio_ext'].includes(key) && data[key]) {
                    this.formData.set(`${key}`, data[key], data[key].name);
                } else {
                    this.formData.set(`${key}`, data[key]);
                }
            }
            this.formData.set('destination_options', JSON.stringify(data.destination_options));
            this.payload = {
                method: HTTP.PUT,
                body: this.formData,
                credentials: 'same-origin',
                headers: {
                    'X-CSRFToken': this.cookies.get('csrftoken')
                }
            };
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
}
