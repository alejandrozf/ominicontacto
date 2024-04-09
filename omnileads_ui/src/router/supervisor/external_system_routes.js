import Index from '@/views/supervisor/external_systems/Index';
import New from '@/views/supervisor/external_systems/New';
import Detail from '@/views/supervisor/external_systems/Detail';
import Edit from '@/views/supervisor/external_systems/Edit';

export default [
    {
        path: '/supervisor_external_systems.html',
        name: 'supervisor_external_systems',
        component: Index
    },
    {
        path: '/supervisor_external_systems/new',
        name: 'supervisor_external_systems_new',
        component: New
    },
    {
        path: '/supervisor_external_systems/:id/edit',
        name: 'supervisor_external_systems_edit',
        component: Edit
    },
    {
        path: '/supervisor_external_systems/:id',
        name: 'supervisor_external_systems_detail',
        component: Detail
    }
];
