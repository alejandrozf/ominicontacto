import Index from '@/views/supervisor/group_of_hours/Index';
import New from '@/views/supervisor/group_of_hours/New';
import Edit from '@/views/supervisor/group_of_hours/Edit';

export default [
    {
        path: '/supervisor_group_of_hours.html',
        name: 'supervisor_group_of_hours',
        component: Index
    },
    {
        path: '/supervisor_group_of_hours/new',
        name: 'supervisor_group_of_hours_new',
        component: New
    },
    {
        path: '/supervisor_group_of_hours/:id/edit',
        name: 'supervisor_group_of_hours_edit',
        component: Edit
    }
];
