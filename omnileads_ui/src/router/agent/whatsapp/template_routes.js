import Index from '@/views/agent/whatsapp/templates/Index';
import { WHATSAPP_URL_NAME } from '@/globals/agent/whatsapp';

export default [
    {
        path: `/${WHATSAPP_URL_NAME}_templates.html`,
        name: `${WHATSAPP_URL_NAME}_templates`,
        component: Index
    }
];
