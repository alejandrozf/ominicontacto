import urls from '../const/form_urls';
import { HTTP, BaseService } from './base_service';

export default class FormService extends BaseService {
    constructor () {
        super(urls, 'Formulario');
    }

    async show (id) {
        try {
            this.setPayload(HTTP.PUT);
            const resp = await fetch(
                urls.Show(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error('Error al desocultar < Formulario >');
            console.error(error);
            return {};
        } finally {
            this.initPayload();
        }
    }

    async hide (id) {
        try {
            this.setPayload(HTTP.PUT);
            const resp = await fetch(
                urls.Hide(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error('Error al ocultar < Formulario >');
            console.error(error);
            return {};
        } finally {
            this.initPayload();
        }
    }
}
