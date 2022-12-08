import apiUrls from '@/api_urls/supervisor/add_agents_to_campaign_urls';
import { HTTP, BaseService } from './../base_service';

export default class AgentsCampaignService extends BaseService {
    async getAgentsByCampaign (idCampaign) {
        try {
            const resp = await fetch(apiUrls.CampaignAgents(idCampaign), this.payload);
            const agentsByCampaign = await resp.json();
            return agentsByCampaign;
        } catch (error) {
            // console.error("No se pudieron obtener los agentes por campaña");
            return [];
        }
    }

    async getActiveAgents () {
        try {
            const resp = await fetch(apiUrls.ActiveAgents, this.payload);
            const agents = await resp.json();
            return agents;
        } catch (error) {
            // console.error("No se pudieron obtener los agentes activos");
            return [];
        }
    }

    async updateAgentsByCampaign (data) {
        try {
            this.setPayload(HTTP.POST, JSON.stringify(data));
            const resp = await fetch(
                apiUrls.UpdateAgentsCampaign,
                this.payload
            );
            this.initPayload();
            return resp;
        } catch (error) {
            // console.error("No se pudieron actualizar los agentes de la campaña");
            // console.error(error);
            return {};
        }
    }
}
