import { getRestWhatsappRoutesByModule } from '@/utils/routes_generator';

export default {
    ...getRestWhatsappRoutesByModule('configuration_whatsapp'),
    CampaignTemplates: (campaignId) => `/api/v1/whatsapp/configuration_whatsapp/templates/${campaignId}`
};
