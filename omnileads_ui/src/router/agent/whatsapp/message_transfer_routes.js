import Index from '@/views/agent/whatsapp/message_transfer/Index';
import { WHATSAPP_URL_NAME } from '@/globals/agent/whatsapp';

export default [
    {
        path: `/${WHATSAPP_URL_NAME}_message_transfer.html`,
        name: `${WHATSAPP_URL_NAME}_message_transfer`,
        component: Index
    }
];
