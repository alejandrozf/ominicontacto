import { getRestWhatsappRoutesByModule } from '@/utils/routes_generator';

export default {
    ...getRestWhatsappRoutesByModule('lines'),
    Campaigns: '/api/v1/whatsapp/campana'
};
