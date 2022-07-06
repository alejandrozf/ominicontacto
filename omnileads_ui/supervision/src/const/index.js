import PauseSetsURL from './pause_sets_urls';
import ExternalSitesUrls from './external_sites_urls';
import CallDispositionUrls from './call_disposition_urls';
import ExternalSystemsUrls from './external_systems_urls';

export default {
    DashboardSupervision: '/api/v1/dashboard_supervision',
    AuditSupervisor: '/api/v1/audit_supervisor',
    CampaignAgents: (idCampaign) => `/api/v1/campaign/${idCampaign}/agents`,
    ActiveAgents: '/api/v1/active_agents',
    UpdateAgentsCampaign: '/api/v1/campaign/agents_update/',
    ...PauseSetsURL,
    ...ExternalSitesUrls,
    ...CallDispositionUrls,
    ...ExternalSystemsUrls
};
