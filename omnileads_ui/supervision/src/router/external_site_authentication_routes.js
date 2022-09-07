import Index from '@/views/external_site_authentications/Index';
import New from '@/views/external_site_authentications/New';
import Edit from '@/views/external_site_authentications/Edit';

export default [
    {
        path: '/external_site_authentications.html',
        name: 'external_site_authentications',
        component: Index
    },
    {
        path: '/external_site_authentications/new',
        name: 'external_site_authentications_new',
        component: New
    },
    {
        path: '/external_site_authentications/:id/update',
        name: 'external_site_authentications_update',
        component: Edit
    }
];
