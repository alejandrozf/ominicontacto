import { createRouter, createWebHistory } from 'vue-router';
import DashboardSupervision from '../views/DashboardSupervision';
import AuditSupervisor from '../views/AuditSupervisor';
import AddAgentsToCampaign from '../views/AddAgentsToCampaign';
import PauseSetRoutes from './pause_set_routes';
import ExternalSiteRoutes from './external_site_routes';
import CallDispositionRoutes from './call_disposition_routes';
import ExternalSystemRoutes from './external_system_routes';
import FormRoutes from './form_routes';
import PauseRoutes from './pause_routes';
import InboundRoutes from './inbound_route_routes';

const routes = [
    {
        path: '/supervision_dashboard.html',
        name: 'supervision_dashboard',
        component: DashboardSupervision
    },
    {
        path: '/security_audit.html',
        name: 'security_audit',
        component: AuditSupervisor
    },
    {
        path: '/add_agents_to_campaign.html',
        name: 'add_agents_to_campaign',
        component: AddAgentsToCampaign
    },
    ...PauseSetRoutes,
    ...ExternalSiteRoutes,
    ...CallDispositionRoutes,
    ...ExternalSystemRoutes,
    ...FormRoutes,
    ...PauseRoutes,
    ...InboundRoutes
];

const router = createRouter({
    history: createWebHistory('/static/omnileads-ui-supervision/'),
    routes
});

export default router;
