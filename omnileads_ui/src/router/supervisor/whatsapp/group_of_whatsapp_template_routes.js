import Index from '@/views/supervisor/whatsapp/group_of_whatsapp_templates/Index';
import New from '@/views/supervisor/whatsapp/group_of_whatsapp_templates/New';
import Edit from '@/views/supervisor/whatsapp/group_of_whatsapp_templates/Edit';
import { WHATSAPP_URL_NAME } from '@/globals/supervisor/whatsapp';

export default [
    {
        path: `/${WHATSAPP_URL_NAME}_group_of_whatsapp_templates.html`,
        name: `${WHATSAPP_URL_NAME}_group_of_whatsapp_templates`,
        component: Index
    },
    {
        path: `/${WHATSAPP_URL_NAME}_group_of_whatsapp_templates/new`,
        name: `${WHATSAPP_URL_NAME}_group_of_whatsapp_templates_new`,
        component: New
    },
    {
        path: `/${WHATSAPP_URL_NAME}_group_of_whatsapp_templates/:id/edit`,
        name: `${WHATSAPP_URL_NAME}_group_of_whatsapp_templates_edit`,
        component: Edit
    }
];
