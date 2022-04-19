import apiUrls from '../const/api-urls';
import { HTTP, BaseService } from './apiBaseService';

export default class PauseSetService extends BaseService {
    async getPauses () {
        try {
            const resp = await fetch(apiUrls.ActivePauses, this.payload);
            return await resp.json();
        } catch (error) {
            console.error('No se pudieron obtener las pausas');
            return [];
        }
    }

    async getPauseSetsList () {
        try {
            const resp = await fetch(apiUrls.PauseSetsList, this.payload);
            return await resp.json();
        } catch (error) {
            console.error('No se pudieron obtener los conjuntos de pausas');
            return [];
        }
    }

    async getPauseSetDetail (id) {
        try {
            const resp = await fetch(apiUrls.PauseSetDetail(id), this.payload);
            return await resp.json();
        } catch (error) {
            console.error('No se pudo obtener el detalle del conjunto de pausas');
            return [];
        }
    }

    async createPauseSet (pauseGroup) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(pauseGroup));
            const resp = await fetch(
                apiUrls.PauseSetCreate,
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo crear el conjunto de pausas');
            console.error(error);
            return {};
        }
    }

    async updatePauseSetName (id, name) {
        try {
            this.setPayload(HTTP.PUT, JSON.stringify(name));
            const resp = await fetch(
                apiUrls.PauseSetUpdate(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo actualizar el conjunto de pausas');
            console.error(error);
            return {};
        }
    }

    async deletePauseSet (id) {
        try {
            this.setPayload(HTTP.DELETE);
            const resp = await fetch(
                apiUrls.PauseSetDelete(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo eliminar el conjunto de pausas');
            return [];
        }
    }

    async createPauseConfig (pauseConfig) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(pauseConfig));
            const resp = await fetch(
                apiUrls.PauseConfigCreate,
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo crear la configuracion de pausa');
            console.error(error);
            return {};
        }
    }

    async updatePauseConfig (id, pauseConfig) {
        try {
            this.setPayload(HTTP.PUT, JSON.stringify(pauseConfig));
            const resp = await fetch(
                apiUrls.PauseConfigUpdate(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo actualizar la configuracion de pausa');
            console.error(error);
            return {};
        }
    }

    async deletePauseConfig (id) {
        try {
            this.setPayload(HTTP.DELETE);
            const resp = await fetch(
                apiUrls.PauseConfigDelete(id),
                this.payload
            );
            this.initPayload();
            return await resp.json();
        } catch (error) {
            console.error('No se pudo eliminar la configuracion de pausa');
            return [];
        }
    }
}
