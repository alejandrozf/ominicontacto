import { getRestRoutesByModule } from '@/utils/routes_generator';

export default {
    ...getRestRoutesByModule('ivrs'),
    IVRAudioOptions: '/api/v1/ivrs/audio_options/',
    IVRDestinations: '/api/v1/ivrs/destination_types/'
};
