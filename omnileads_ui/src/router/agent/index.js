import WhatsappAgentRoutes from './whatsapp';
import FacebookAgentRoutes from './facebook';

export const agentRoutes = [
    ...WhatsappAgentRoutes,
    ...FacebookAgentRoutes
];
