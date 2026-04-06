import Index from '@/views/agent/facebook/templates/Index';
import { FACEBOOK_URL_NAME } from '@/globals/agent/facebook';

export default [
    {
        path: `/${FACEBOOK_URL_NAME}_templates.html`,
        name: `${FACEBOOK_URL_NAME}_templates`,
        component: Index
    }
];
