export default {
    List: '/api/v1/inbound_routes',
    Create: '/api/v1/inbound_routes/create/',
    Detail: (id) => `/api/v1/inbound_routes/${id}`,
    Delete: (id) => `/api/v1/inbound_routes/${id}/delete`,
    Update: (id) => `/api/v1/inbound_routes/${id}/update/`,
    InboundRouteDestinationsByType: '/api/v1/inbound_routes/destinations_by_type'
};
