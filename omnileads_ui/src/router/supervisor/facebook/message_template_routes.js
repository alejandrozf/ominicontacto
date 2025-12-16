import Index from '@/views/supervisor/facebook/message_templates/Index';
import { FACEBOOK_URL_NAME } from '@/globals/supervisor/facebook';

export default [
    {
        path: `/${FACEBOOK_URL_NAME}_message_templates.html`,
        name: `${FACEBOOK_URL_NAME}_message_templates`,
        component: Index
    }
];
