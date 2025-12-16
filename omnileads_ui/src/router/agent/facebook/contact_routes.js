import Index from '@/views/agent/facebook/contact/Index';
import { FACEBOOK_URL_NAME } from '@/globals/agent/facebook';

export default [
    {
        path: `/${FACEBOOK_URL_NAME}_contact_form.html`,
        name: `${FACEBOOK_URL_NAME}_contact_form`,
        component: Index
    }
];
