import Index from '@/views/agent/facebook/Index';
import ConversationRoutes from './conversation_routes';
import TemplateRoutes from './template_routes';
import DispositionChatRoutes from './disposition_chat_routes';
import MessageTransferRoutes from './message_transfer_routes';
import ContactRoutes from './contact_routes';
import { FACEBOOK_URL_NAME } from '@/globals/agent/facebook';

export default [
    {
        path: `/${FACEBOOK_URL_NAME}_index.html`,
        name: `${FACEBOOK_URL_NAME}`,
        component: Index
    },
    ...ConversationRoutes,
    ...TemplateRoutes,
    ...DispositionChatRoutes,
    ...MessageTransferRoutes,
    ...ContactRoutes
];
