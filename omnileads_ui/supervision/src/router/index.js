import { createRouter, createWebHistory } from 'vue-router';
import DashboardSupervision from '../views/DashboardSupervision';
import AuditSupervisor from '../views/AuditSupervisor';
import AddAgentsToCampaign from '../views/AddAgentsToCampaign';
import PauseSetRoutes from './pause_sets_routes';

const routes = [
    {
        path: '/audit.html',
        name: 'audit_supervisor',
        component: AuditSupervisor
    },
    {
        path: '/dashboard.html',
        name: 'dashboard',
        component: DashboardSupervision
    },
    {
        path: '/add_agents_to_campaign.html',
        name: 'add_agents_to_campaign',
        component: AddAgentsToCampaign
    },
    ...PauseSetRoutes
];

const router = createRouter({
    history: createWebHistory('/static/omnileads-ui-supervision/'),
    routes
});

export default router;
