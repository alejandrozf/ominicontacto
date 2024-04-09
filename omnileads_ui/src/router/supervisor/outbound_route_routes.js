import Index from '@/views/supervisor/outbound_routes/Index';
import New from '@/views/supervisor/outbound_routes/New';
import Edit from '@/views/supervisor/outbound_routes/Edit';

export default [
    {
        path: '/supervisor_outbound_routes.html',
        name: 'supervisor_outbound_routes',
        component: Index
    },
    {
        path: '/supervisor_outbound_routes/new',
        name: 'supervisor_outbound_routes_new',
        component: New
    },
    {
        path: '/supervisor_outbound_routes/:id/edit',
        name: 'supervisor_outbound_routes_edit',
        component: Edit
    }
];
