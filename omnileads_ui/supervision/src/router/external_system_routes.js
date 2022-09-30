import Index from '@/views/external_systems/Index';
import New from '@/views/external_systems/New';
import Detail from '@/views/external_systems/Detail';
import Edit from '@/views/external_systems/Edit';

export default [
    {
        path: '/external_systems.html',
        name: 'external_systems',
        component: Index
    },
    {
        path: '/external_systems/new',
        name: 'external_systems_new',
        component: New
    },
    {
        path: '/external_systems/:id/edit',
        name: 'external_systems_edit',
        component: Edit
    },
    {
        path: '/external_systems/:id',
        name: 'external_systems_detail',
        component: Detail
    }
];
