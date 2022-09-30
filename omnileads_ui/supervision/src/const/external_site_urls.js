export default {
    List: '/api/v1/external_sites',
    Create: '/api/v1/external_sites/create/',
    Detail: (id) => `/api/v1/external_sites/${id}`,
    Update: (id) => `/api/v1/external_sites/${id}/update/`,
    Delete: (id) => `/api/v1/external_sites/${id}/delete`,
    Hide: (id) => `/api/v1/external_sites/${id}/hide/`,
    Show: (id) => `/api/v1/external_sites/${id}/show/`
};
