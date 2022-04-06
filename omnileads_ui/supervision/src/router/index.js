import { createRouter, createWebHistory } from 'vue-router';
import DashboardSupervision from '../views/DashboardSupervision';
import AuditSupervisor from '../views/AuditSupervisor';
import AddAgentsToCampaign from '../views/AddAgentsToCampaign';

const routes = [
    {
        path: '/',
        name: 'dashboard',
        component: DashboardSupervision
    },
    {
        path: '/index.html',
        name: 'dashboard',
        component: DashboardSupervision
    },
    {
        path: '/index.html',
        name: 'dashboard',
        component: DashboardSupervision
    },
    {
        path: '/audit.html',
        name: 'audit_supervisor',
        component: AuditSupervisor
    },
    {
        path: '/add_agents_to_campaign.html',
        name: 'add_agents_to_campaign',
        component: AddAgentsToCampaign
    }
];

const router = createRouter({
    history: createWebHistory('/static/omnileads-ui-supervision/'),
    routes
});

export default router;
