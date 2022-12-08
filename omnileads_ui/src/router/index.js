import { createRouter, createWebHistory } from 'vue-router';
import { supervisorRoutes } from './supervisor';
import { agentRoutes } from './agent';

const routes = [
    ...supervisorRoutes,
    ...agentRoutes
];

const router = createRouter({
    history: createWebHistory('/static/omnileads-frontend/'),
    routes
});

export default router;
