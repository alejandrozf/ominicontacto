import Index from '@/views/forms/Index';
import New from '@/views/forms/New';
import Detail from '@/views/forms/Detail';
import Edit from '@/views/forms/Edit';
import Step1 from '@/components/forms/form_steps/Step1';
import Step2 from '@/components/forms/form_steps/Step2';
import Step3 from '@/components/forms/form_steps/Step3';

export default [
    {
        path: '/forms.html',
        name: 'forms',
        component: Index
    },
    {
        path: '/forms/new',
        name: 'forms_new',
        component: New,
        children: [
            {
                path: 'step1',
                name: 'forms_new_step1',
                component: Step1
            },
            {
                path: 'step2',
                name: 'forms_new_step2',
                component: Step2
            },
            {
                path: 'step3',
                name: 'forms_new_step3',
                component: Step3
            }
        ]
    },
    {
        path: '/forms/:id/edit',
        name: 'forms_edit',
        component: Edit,
        children: [
            {
                path: 'step1',
                name: 'forms_edit_step1',
                component: Step1
            },
            {
                path: 'step2',
                name: 'forms_edit_step2',
                component: Step2
            },
            {
                path: 'step3',
                name: 'forms_edit_step3',
                component: Step3
            }
        ]
    },
    {
        path: '/forms/:id',
        name: 'forms_detail',
        component: Detail
    }
];
