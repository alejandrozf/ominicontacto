import Index from '@/views/supervisor/ivrs/Index';
import New from '@/views/supervisor/ivrs/New';
import Edit from '@/views/supervisor/ivrs/Edit';

export default [
    {
        path: '/supervisor_ivrs.html',
        name: 'supervisor_ivrs',
        component: Index
    },
    {
        path: '/supervisor_ivrs/new',
        name: 'supervisor_ivrs_new',
        component: New
    },
    {
        path: '/supervisor_ivrs/:id/edit',
        name: 'supervisor_ivrs_edit',
        component: Edit
    }
];
