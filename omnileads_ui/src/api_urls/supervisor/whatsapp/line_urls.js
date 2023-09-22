import { getRestWhatsappRoutesByModule } from '@/utils/routes_generator';

export default {
    ...getRestWhatsappRoutesByModule('line'),
    Campaigns: '/api/v1/whatsapp/campaing'
};
