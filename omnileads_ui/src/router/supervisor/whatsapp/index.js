import Index from '@/views/supervisor/whatsapp/Index';
import ProviderRoutes from './provider_routes';
import LineRoutes from './line_routes';
import MessageTemlateRoutes from './message_template_routes';
import { WHATSAPP_URL_NAME } from '@/globals/supervisor/whatsapp';

export default [
    {
        path: `/${WHATSAPP_URL_NAME}.html`,
        name: `${WHATSAPP_URL_NAME}`,
        component: Index
    },
    ...ProviderRoutes,
    ...LineRoutes,
    ...MessageTemlateRoutes
];
