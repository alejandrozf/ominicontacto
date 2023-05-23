import Index from '@/views/agent/whatsapp/disposition_form/Index';
import { WHATSAPP_URL_NAME } from '@/globals/agent/whatsapp';

export default [
    {
        path: `/${WHATSAPP_URL_NAME}_disposition_form.html`,
        name: `${WHATSAPP_URL_NAME}_disposition_form`,
        component: Index
    }
];
