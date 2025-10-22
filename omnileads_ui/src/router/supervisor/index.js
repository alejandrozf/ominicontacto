import SupervisionDashboardRoutes from './supervision_dashboard_routes';
import AuditSupervisionRoutes from './audit_routes';
import AddAgentsToCampaignRoutes from './add_agents_to_campaign_routes';
import PauseSetRoutes from './pause_set_routes';
import ExternalSiteRoutes from './external_site_routes';
import ExternalSiteAuthenticationRoutes from './external_site_authentication_routes';
import CallDispositionRoutes from './call_disposition_routes';
import ExternalSystemRoutes from './external_system_routes';
import FormRoutes from './form_routes';
import PauseRoutes from './pause_routes';
import InboundRoutes from './inbound_route_routes';
import OutboundRoutes from './outbound_route_routes';
import GroupOfHourRoutes from './group_of_hour_routes';
import IVRRoutes from './ivr_routes';
import RegisterServerRoutes from './register_server_routes';
import WhatsAppRoutes from './whatsapp';
import FacebookRoutes from './facebook';

export const supervisorRoutes = [
    ...SupervisionDashboardRoutes,
    ...AuditSupervisionRoutes,
    ...AddAgentsToCampaignRoutes,
    ...PauseSetRoutes,
    ...ExternalSiteRoutes,
    ...ExternalSiteAuthenticationRoutes,
    ...CallDispositionRoutes,
    ...ExternalSystemRoutes,
    ...FormRoutes,
    ...PauseRoutes,
    ...InboundRoutes,
    ...OutboundRoutes,
    ...GroupOfHourRoutes,
    ...IVRRoutes,
    ...RegisterServerRoutes,
    ...WhatsAppRoutes,
    ...FacebookRoutes
];
