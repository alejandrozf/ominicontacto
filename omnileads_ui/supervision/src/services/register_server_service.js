import urls from '../const/register_server_urls';
import { BaseService, HTTP } from './base_service';

export default class RegisterServerService extends BaseService {
    constructor () {
        super(urls, 'Register Server');
    }

    async resendKey () {
        try {
            this.setPayload(HTTP.POST, JSON.stringify({}));
            const resp = await fetch(
                urls.ResendKey, this.payload);
            return await resp.json();
        } catch (error) {
            console.error('Error al reenviar el Key < Register Server >');
            return null;
        } finally {
            this.initPayload();
        }
    }

    async registerInfo () {
        try {
            this.setPayload(HTTP.GET);
            const resp = await fetch(
                urls.RegisterInfo, this.payload);
            return await resp.json();
        } catch (error) {
            console.error('Error al obtener informacion < Register Server >');
            return null;
        } finally {
            this.initPayload();
        }
    }
}
