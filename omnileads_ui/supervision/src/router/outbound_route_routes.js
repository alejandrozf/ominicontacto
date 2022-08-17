import Index from '@/views/outbound_routes/Index';
import New from '@/views/outbound_routes/New';
import Edit from '@/views/outbound_routes/Edit';

export default [
    {
        path: '/outbound_routes.html',
        name: 'outbound_routes',
        component: Index
    },
    {
        path: '/outbound_routes/new',
        name: 'outbound_routes_new',
        component: New
    },
    {
        path: '/outbound_routes/:id/edit',
        name: 'outbound_routes_edit',
        component: Edit
    }
];
