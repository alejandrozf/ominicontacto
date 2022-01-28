import { createRouter, createWebHistory } from 'vue-router';
import DashboardSupervision from '../views/DashboardSupervision';
import AuditSupervisor from '../views/AuditSupervisor';

const routes = [
    {
        path: '/index.html',
        name: 'dashboard',
        component: DashboardSupervision,
    },
    {
        path: '/audit.html',
        name: 'audit_supervisor',
        component: AuditSupervisor,
    },  
];
const router = createRouter({
    history: createWebHistory('/static/omnileads-ui-supervision/'),
    routes
});

export default router;
