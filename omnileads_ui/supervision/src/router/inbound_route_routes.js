import Index from '@/views/inbound_routes/Index';
import New from '@/views/inbound_routes/New';
import Edit from '@/views/inbound_routes/Edit';

export default [
    {
        path: '/inbound_routes.html',
        name: 'inbound_routes',
        component: Index
    },
    {
        path: '/inbound_routes/new',
        name: 'inbound_routes_new',
        component: New
    },
    {
        path: '/inbound_routes/:id/edit',
        name: 'inbound_routes_edit',
        component: Edit
    }
];
