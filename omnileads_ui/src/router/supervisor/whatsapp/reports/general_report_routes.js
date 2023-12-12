import Index from '@/views/supervisor/whatsapp/reports/general/Index';
import { WHATSAPP_REPORTS_URL_NAME } from '@/globals/supervisor/whatsapp';

export default [
    {
        path: `/${WHATSAPP_REPORTS_URL_NAME}_general.html`,
        name: `${WHATSAPP_REPORTS_URL_NAME}_general`,
        component: Index
    }
];
