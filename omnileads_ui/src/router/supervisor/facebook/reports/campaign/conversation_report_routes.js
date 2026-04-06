import Index from '@/views/supervisor/facebook/reports/campaign/conversation_report/Index';
import { FACEBOOK_REPORTS_URL_NAME } from '@/globals/supervisor/facebook';

export default [
    {
        path: `/${FACEBOOK_REPORTS_URL_NAME}_campaign_conversations.html`,
        name: `${FACEBOOK_REPORTS_URL_NAME}_campaign_conversations`,
        component: Index
    }
];
