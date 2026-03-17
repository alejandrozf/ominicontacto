import Index from '@/views/supervisor/facebook/reports/general/Index';
import { FACEBOOK_REPORTS_URL_NAME } from '@/globals/supervisor/facebook';

export default [
    {
        path: `/${FACEBOOK_REPORTS_URL_NAME}_general.html`,
        name: `${FACEBOOK_REPORTS_URL_NAME}_general`,
        component: Index
    }
];
