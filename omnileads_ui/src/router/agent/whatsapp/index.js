import Index from '@/views/agent/whatsapp/Index';
import ConversationRoutes from './conversation_routes';
import TemplateRoutes from './template_routes';
import DispositionFormRoutes from './disposition_form_routes';
import MessageTransferRoutes from './message_transfer_routes';
import { WHATSAPP_URL_NAME } from '@/globals/agent/whatsapp';

export default [
    {
        path: `/${WHATSAPP_URL_NAME}_index.html`,
        name: `${WHATSAPP_URL_NAME}`,
        component: Index
    },
    ...ConversationRoutes,
    ...TemplateRoutes,
    ...DispositionFormRoutes,
    ...MessageTransferRoutes
];
