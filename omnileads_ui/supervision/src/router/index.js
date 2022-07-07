import { createRouter, createWebHistory } from 'vue-router';
import DashboardSupervision from '../views/DashboardSupervision';
import AuditSupervisor from '../views/AuditSupervisor';
import AddAgentsToCampaign from '../views/AddAgentsToCampaign';
import PauseSetRoutes from './pause_sets_routes';
import ExternalSitesRoutes from './external_sites_routes';
import CallDispositionRoutes from './call_dispositions_routes';
import ExternalSystemRoutes from './external_systems_routes';

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
    ...ExternalSitesRoutes,
    ...CallDispositionRoutes,
    ...ExternalSystemRoutes
];

const router = createRouter({
    history: createWebHistory('/static/omnileads-ui-supervision'),
    routes
});

export default router;
