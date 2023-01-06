import Index from '@/views/ivrs/Index';
import New from '@/views/ivrs/New';
import Edit from '@/views/ivrs/Edit';

export default [
    {
        path: '/ivrs.html',
        name: 'ivrs',
        component: Index
    },
    {
        path: '/ivrs/new',
        name: 'ivrs_new',
        component: New
    },
    {
        path: '/ivrs/:id/edit',
        name: 'ivrs_edit',
        component: Edit
    }
];
