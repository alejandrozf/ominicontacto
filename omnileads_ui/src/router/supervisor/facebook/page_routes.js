import Index from '@/views/supervisor/facebook/pages/Index';
import New from '@/views/supervisor/facebook/pages/New';
import Edit from '@/views/supervisor/facebook/pages/Edit';
import WhatsappTemplateIndex from '@/views/supervisor/whatsapp/whatsapp_templates/Index';
import Step1 from '@/components/supervisor/facebook/pages/form_steps/Step1';
import Step2 from '@/components/supervisor/facebook/pages/form_steps/Step2';
import Step3 from '@/components/supervisor/facebook/pages/form_steps/Step3';
import { FACEBOOK_URL_NAME } from '@/globals/supervisor/facebook';

export default [
    {
        path: `/${FACEBOOK_URL_NAME}_pages.html`,
        name: `${FACEBOOK_URL_NAME}_pages`,
        component: Index
    },
    {
        path: `/${FACEBOOK_URL_NAME}_pages/new`,
        name: `${FACEBOOK_URL_NAME}_pages_new`,
        component: New,
        children: [
            {
                path: 'step1',
                name: `${FACEBOOK_URL_NAME}_pages_new_step1`,
                component: Step1
            },
            {
                path: 'step2',
                name: `${FACEBOOK_URL_NAME}_pages_new_step2`,
                component: Step2
            },
            {
                path: 'step3',
                name: `${FACEBOOK_URL_NAME}_pages_new_step3`,
                component: Step3
            }
        ]
    },
    {
        path: `/${FACEBOOK_URL_NAME}_pages/:id/edit`,
        name: `${FACEBOOK_URL_NAME}_pages_edit`,
        component: Edit,
        children: [
            {
                path: 'step1',
                name: `${FACEBOOK_URL_NAME}_pages_edit_step1`,
                component: Step1
            },
            {
                path: 'step2',
                name: `${FACEBOOK_URL_NAME}_pages_edit_step2`,
                component: Step2
            },
            {
                path: 'step3',
                name: `${FACEBOOK_URL_NAME}_pages_edit_step3`,
                component: Step3
            }
        ]
    },
    {
        path: `/${FACEBOOK_URL_NAME}_pages/:id/whatsapp_templates`,
        name: `${FACEBOOK_URL_NAME}_pages_whatsapp_templates`,
        component: WhatsappTemplateIndex
    }
];
