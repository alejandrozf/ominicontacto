import Index from '@/views/supervisor/whatsapp/Index';
import PageRoutes from './page_routes';
import MessageTemplateRoutes from './message_template_routes';
import GroupOfMessageTemlateRoutes from './group_of_message_template_routes';
import { FACEBOOK_URL_NAME } from '@/globals/supervisor/facebook';

export default [
    {
        path: `/${FACEBOOK_URL_NAME}.html`,
        name: `${FACEBOOK_URL_NAME}`,
        component: Index
    },
    ...PageRoutes,
    ...MessageTemplateRoutes,
    ...GroupOfMessageTemlateRoutes
];
