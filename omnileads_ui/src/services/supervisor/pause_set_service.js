import urls from '@/api_urls/supervisor/pause_set_urls';
import { HTTP, BaseService } from './../base_service';

export default class PauseSetService extends BaseService {
    constructor () {
        super(urls, 'Conjunto de Pausa');
    }

    async getPauses () {
        try {
            const resp = await fetch(urls.ActivePauses, this.payload);
            return await resp.json();
        } catch (error) {
            console.error('No se pudieron obtener las pausas');
            return [];
        }
    }

    async createPauseConfig (pauseConfig) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(pauseConfig));
            const resp = await fetch(
                urls.PauseConfigCreate,
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error('Error al crear < Configuracion de Pausa >');
            console.error(error);
            return {};
        } finally {
            this.initPayload();
        }
    }

    async updatePauseConfig (id, pauseConfig) {
        try {
            this.setPayload(HTTP.PUT, JSON.stringify(pauseConfig));
            const resp = await fetch(
                urls.PauseConfigUpdate(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error('Error al actualizar < Configuracion de Pausa >');
            console.error(error);
            return {};
        } finally {
            this.initPayload();
        }
    }

    async deletePauseConfig (id) {
        try {
            this.setPayload(HTTP.DELETE);
            const resp = await fetch(
                urls.PauseConfigDelete(id),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error('Error al eliminar < Configuracion de Pausa >');
            return [];
        } finally {
            this.initPayload();
        }
    }
}
