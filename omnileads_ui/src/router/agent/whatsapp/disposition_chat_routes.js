import Index from '@/views/agent/whatsapp/disposition_chat/Index';
import { WHATSAPP_URL_NAME } from '@/globals/agent/whatsapp';

export default [
    {
        path: `/${WHATSAPP_URL_NAME}_disposition_chat.html`,
        name: `${WHATSAPP_URL_NAME}_disposition_chat`,
        component: Index
    }
];
