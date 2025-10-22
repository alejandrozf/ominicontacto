import { getRestFacebookRoutesByModule } from '@/utils/routes_generator';

export default {
    ...getRestFacebookRoutesByModule('page'),
    Campaigns: '/api/v1/facebook/campaigns'
};
