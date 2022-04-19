import Index from '@/views/pause_sets/Index';
import Detail from '@/views/pause_sets/Detail';
import New from '@/views/pause_sets/New';

export default [
    {
        path: '/pause_sets.html',
        name: 'pause_sets',
        component: Index
    },
    {
        path: '/pause_sets/new',
        name: 'pause_sets_new',
        component: New
    },
    {
        path: '/pause_sets/:id',
        name: 'pause_sets_detail',
        component: Detail
    }
];
