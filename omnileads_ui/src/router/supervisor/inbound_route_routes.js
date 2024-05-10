import Index from '@/views/supervisor/inbound_routes/Index';
import New from '@/views/supervisor/inbound_routes/New';
import Edit from '@/views/supervisor/inbound_routes/Edit';

export default [
    {
        path: '/supervisor_inbound_routes.html',
        name: 'supervisor_inbound_routes',
        component: Index
    },
    {
        path: '/supervisor_inbound_routes/new',
        name: 'supervisor_inbound_routes_new',
        component: New
    },
    {
        path: '/supervisor_inbound_routes/:id/edit',
        name: 'supervisor_inbound_routes_edit',
        component: Edit
    }
];
