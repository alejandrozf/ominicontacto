import PauseSetsURL from './pause_set_urls';
import ExternalSiteUrls from './external_site_urls';
import CallDispositionUrls from './call_disposition_urls';
import ExternalSystemUrls from './external_system_urls';
import FormUrls from './form_urls';

export default {
    DashboardSupervision: '/api/v1/dashboard_supervision',
    AuditSupervisor: '/api/v1/audit_supervisor',
    CampaignAgents: (idCampaign) => `/api/v1/campaign/${idCampaign}/agents`,
    ActiveAgents: '/api/v1/active_agents',
    UpdateAgentsCampaign: '/api/v1/campaign/agents_update/',
    ...PauseSetsURL,
    ...ExternalSiteUrls,
    ...CallDispositionUrls,
    ...ExternalSystemUrls,
    ...FormUrls
};
