import Index from '@/views/supervisor/forms/Index';
import New from '@/views/supervisor/forms/New';
import Detail from '@/views/supervisor/forms/Detail';
import Edit from '@/views/supervisor/forms/Edit';
import Step1 from '@/components/supervisor/forms/form_steps/Step1';
import Step2 from '@/components/supervisor/forms/form_steps/Step2';
import Step3 from '@/components/supervisor/forms/form_steps/Step3';

export default [
    {
        path: '/supervisor_forms.html',
        name: 'supervisor_forms',
        component: Index
    },
    {
        path: '/supervisor_forms/new',
        name: 'supervisor_forms_new',
        component: New,
        children: [
            {
                path: 'step1',
                name: 'supervisor_forms_new_step1',
                component: Step1
            },
            {
                path: 'step2',
                name: 'supervisor_forms_new_step2',
                component: Step2
            },
            {
                path: 'step3',
                name: 'supervisor_forms_new_step3',
                component: Step3
            }
        ]
    },
    {
        path: '/supervisor_forms/:id/edit',
        name: 'supervisor_forms_edit',
        component: Edit,
        children: [
            {
                path: 'step1',
                name: 'supervisor_forms_edit_step1',
                component: Step1
            },
            {
                path: 'step2',
                name: 'supervisor_forms_edit_step2',
                component: Step2
            },
            {
                path: 'step3',
                name: 'supervisor_forms_edit_step3',
                component: Step3
            }
        ]
    },
    {
        path: '/supervisor_forms/:id',
        name: 'supervisor_forms_detail',
        component: Detail
    }
];
