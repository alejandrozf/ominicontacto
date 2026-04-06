import Index from '@/views/agent/facebook/message_transfer/Index';
import { FACEBOOK_URL_NAME } from '@/globals/agent/facebook';

export default [
    {
        path: `/${FACEBOOK_URL_NAME}_message_transfer.html`,
        name: `${FACEBOOK_URL_NAME}_message_transfer`,
        component: Index
    }
];
