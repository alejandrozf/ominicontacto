import Index from '@/views/group_of_hours/Index';
import New from '@/views/group_of_hours/New';
import Edit from '@/views/group_of_hours/Edit';

export default [
    {
        path: '/group_of_hours.html',
        name: 'group_of_hours',
        component: Index
    },
    {
        path: '/group_of_hours/new',
        name: 'group_of_hours_new',
        component: New
    },
    {
        path: '/group_of_hours/:id/edit',
        name: 'group_of_hours_edit',
        component: Edit
    }
];
