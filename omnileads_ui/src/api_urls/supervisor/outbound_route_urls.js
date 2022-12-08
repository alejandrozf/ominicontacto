export default {
    List: '/api/v1/outbound_routes',
    Create: '/api/v1/outbound_routes/create/',
    Detail: (id) => `/api/v1/outbound_routes/${id}`,
    Delete: (id) => `/api/v1/outbound_routes/${id}/delete`,
    Update: (id) => `/api/v1/outbound_routes/${id}/update/`,
    OutboundRouteOrphanTrunks: (id) => `/api/v1/outbound_routes/${id}/orphan_trunks`,
    OutboundRouteSipTrunks: '/api/v1/outbound_routes/sip_trunks',
    OutboundRouteReorder: '/api/v1/outbound_routes/reorder/'
};
