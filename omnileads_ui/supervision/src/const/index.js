import PauseSetsURL from './pause_sets_urls';
import ExternalSiteUrls from './external_sites_urls';

export default {
    DashboardSupervision: '/api/v1/dashboard_supervision',
    AuditSupervisor: '/api/v1/audit_supervisor',
    CampaignAgents: (idCampaign) => `/api/v1/campaign/${idCampaign}/agents`,
    ActiveAgents: '/api/v1/active_agents',
    UpdateAgentsCampaign: '/api/v1/campaign/agents_update/',
    ...PauseSetsURL,
    ...ExternalSiteUrls
};
