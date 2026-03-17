import URLS from '@/api_urls/agent/facebook/transfer_urls';
import { BaseService, HTTP } from '@/services/base_service';

export default class FacebookTransferChatService extends BaseService {
    constructor () {
        super(URLS, 'Facebook < Transfer Chat >');
    }

    async getActiveAgents ({ campaingId }) {
        try {
            const resp = await fetch(
                this.urls.agentList(campaingId),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener Agentes`);
            return [];
        } finally {
            this.initPayload();
        }
    }

    async transferToagent (data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                this.urls.transferToagent(),
                this.payload
            );
            return await resp.json();
        } catch (error) {
            console.error(`Error al obtener Agentes`);
            return [];
        } finally {
            this.initPayload();
        }
    }
}
