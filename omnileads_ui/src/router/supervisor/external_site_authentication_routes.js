import Index from '@/views/supervisor/external_site_authentications/Index';
import New from '@/views/supervisor/external_site_authentications/New';
import Edit from '@/views/supervisor/external_site_authentications/Edit';

export default [
    {
        path: '/supervisor_external_site_authentications.html',
        name: 'supervisor_external_site_authentications',
        component: Index
    },
    {
        path: '/supervisor_external_site_authentications/new',
        name: 'supervisor_external_site_authentications_new',
        component: New
    },
    {
        path: '/supervisor_external_site_authentications/:id/update',
        name: 'supervisor_external_site_authentications_update',
        component: Edit
    }
];
