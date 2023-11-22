import { getRestWhatsappRoutesByModule } from '@/utils/routes_generator';

export default {
    ...getRestWhatsappRoutesByModule('templates_whatsapp'),
    SyncUp: (id) => `/api/v1/whatsapp/templates_whatsapp/sincronizar_templates/${id}`,
    StatusChange: (templateId, lineId) => `/api/v1/whatsapp/templates_whatsapp/${templateId}/status_change/${lineId}`
};
