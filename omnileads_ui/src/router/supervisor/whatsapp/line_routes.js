import Index from '@/views/supervisor/whatsapp/lines/Index';
import New from '@/views/supervisor/whatsapp/lines/New';
import Edit from '@/views/supervisor/whatsapp/lines/Edit';
import Step1 from '@/components/supervisor/whatsapp/lines/form_steps/Step1';
import Step2 from '@/components/supervisor/whatsapp/lines/form_steps/Step2';
import Step3 from '@/components/supervisor/whatsapp/lines/form_steps/Step3';
import { WHATSAPP_URL_NAME } from '@/globals/supervisor/whatsapp';

export default [
    {
        path: `/${WHATSAPP_URL_NAME}_lines.html`,
        name: `${WHATSAPP_URL_NAME}_lines`,
        component: Index
    },
    {
        path: `/${WHATSAPP_URL_NAME}_lines/new`,
        name: `${WHATSAPP_URL_NAME}_lines_new`,
        component: New,
        children: [
            {
                path: 'step1',
                name: `${WHATSAPP_URL_NAME}_lines_new_step1`,
                component: Step1
            },
            {
                path: 'step2',
                name: `${WHATSAPP_URL_NAME}_lines_new_step2`,
                component: Step2
            },
            {
                path: 'step3',
                name: `${WHATSAPP_URL_NAME}_lines_new_step3`,
                component: Step3
            }
        ]
    },
    {
        path: `/${WHATSAPP_URL_NAME}_lines/:id/edit`,
        name: `${WHATSAPP_URL_NAME}_lines_edit`,
        component: Edit,
        children: [
            {
                path: 'step1',
                name: `${WHATSAPP_URL_NAME}_lines_edit_step1`,
                component: Step1
            },
            {
                path: 'step2',
                name: `${WHATSAPP_URL_NAME}_lines_edit_step2`,
                component: Step2
            },
            {
                path: 'step3',
                name: `${WHATSAPP_URL_NAME}_lines_edit_step3`,
                component: Step3
            }
        ]
    }
];
