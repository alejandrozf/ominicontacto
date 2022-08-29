export function getRestRoutesByModule (module) {
    return {
        List: `/api/v1/${module}`,
        Create: `/api/v1/${module}/create/`,
        Detail: (id) => `/api/v1/${module}/${id}`,
        Delete: (id) => `/api/v1/${module}/${id}/delete`,
        Update: (id) => `/api/v1/${module}/${id}/update/`
    };
}
