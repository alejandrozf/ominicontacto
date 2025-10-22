import Index from '@/views/supervisor/whatsapp/reports/campaign/conversation_report/Index';
import { WHATSAPP_REPORTS_URL_NAME } from '@/globals/supervisor/whatsapp';

export default [
    {
        path: `/${WHATSAPP_REPORTS_URL_NAME}_campaign_conversations.html`,
        name: `${WHATSAPP_REPORTS_URL_NAME}_campaign_conversations`,
        component: Index
    }
];
