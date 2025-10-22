import Index from '@/views/supervisor/whatsapp/message_templates/Index';
import { WHATSAPP_URL_NAME } from '@/globals/supervisor/whatsapp';

export default [
    {
        path: `/${WHATSAPP_URL_NAME}_message_templates.html`,
        name: `${WHATSAPP_URL_NAME}_message_templates`,
        component: Index
    }
];
