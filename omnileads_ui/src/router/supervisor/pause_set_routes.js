import Index from '@/views/supervisor/pause_sets/Index';
import Detail from '@/views/supervisor/pause_sets/Detail';
import New from '@/views/supervisor/pause_sets/New';

export default [
    {
        path: '/supervisor_pause_sets.html',
        name: 'supervisor_pause_sets',
        component: Index
    },
    {
        path: '/supervisor_pause_sets/new',
        name: 'supervisor_pause_sets_new',
        component: New
    },
    {
        path: '/supervisor_pause_sets/:id',
        name: 'supervisor_pause_sets_detail',
        component: Detail
    }
];
