import Index from '@/views/external_sites/Index';
import New from '@/views/external_sites/New';
import Edit from '@/views/external_sites/Edit';

export default [
    {
        path: '/external_sites.html',
        name: 'external_sites',
        component: Index
    },
    {
        path: '/external_sites/new',
        name: 'external_sites_new',
        component: New
    },
    {
        path: '/external_sites/:id/update',
        name: 'external_sites_update',
        component: Edit
    }
];
