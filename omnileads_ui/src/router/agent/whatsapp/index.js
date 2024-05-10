import Index from '@/views/agent/whatsapp/Index';
import ConversationRoutes from './conversation_routes';
import TemplateRoutes from './template_routes';
import DispositionChatRoutes from './disposition_chat_routes';
import MessageTransferRoutes from './message_transfer_routes';
import ContactRoutes from './contact_routes';
import { WHATSAPP_URL_NAME } from '@/globals/agent/whatsapp';

export default [
    {
        path: `/${WHATSAPP_URL_NAME}_index.html`,
        name: `${WHATSAPP_URL_NAME}`,
        component: Index
    },
    ...ConversationRoutes,
    ...TemplateRoutes,
    ...DispositionChatRoutes,
    ...MessageTransferRoutes,
    ...ContactRoutes
];
