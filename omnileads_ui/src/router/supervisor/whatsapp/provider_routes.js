import Index from '@/views/supervisor/whatsapp/providers/Index';
import { WHATSAPP_URL_NAME } from '@/globals/supervisor/whatsapp';

export default [
    {
        path: `/${WHATSAPP_URL_NAME}_providers.html`,
        name: `${WHATSAPP_URL_NAME}_providers`,
        component: Index
    }
];
