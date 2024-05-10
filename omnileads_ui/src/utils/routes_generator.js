export function getRestRoutesByModule (module) {
    return {
        List: `/api/v1/${module}`,
        Create: `/api/v1/${module}/create/`,
        Detail: (id) => `/api/v1/${module}/${id}`,
        Delete: (id) => `/api/v1/${module}/${id}/delete`,
        Update: (id) => `/api/v1/${module}/${id}/update/`
    };
}

export function getRestWhatsappRoutesByModule (module) {
    return {
        List: `/api/v1/whatsapp/${module}`,
        Create: `/api/v1/whatsapp/${module}`,
        Detail: (id) => `/api/v1/whatsapp/${module}/${id}`,
        Delete: (id) => `/api/v1/whatsapp/${module}/${id}`,
        Update: (id) => `/api/v1/whatsapp/${module}/${id}`
    };
}
