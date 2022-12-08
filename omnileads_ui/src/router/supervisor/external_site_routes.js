import Index from '@/views/supervisor/external_sites/Index';
import New from '@/views/supervisor/external_sites/New';
import Edit from '@/views/supervisor/external_sites/Edit';

export default [
    {
        path: '/supervisor_external_sites.html',
        name: 'supervisor_external_sites',
        component: Index
    },
    {
        path: '/supervisor_external_sites/new',
        name: 'supervisor_external_sites_new',
        component: New
    },
    {
        path: '/supervisor_external_sites/:id/update',
        name: 'supervisor_external_sites_update',
        component: Edit
    }
];
