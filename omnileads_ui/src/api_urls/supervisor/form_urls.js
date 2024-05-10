export default {
    List: '/api/v1/forms',
    Create: '/api/v1/forms/create/',
    Detail: (id) => `/api/v1/forms/${id}`,
    Delete: (id) => `/api/v1/forms/${id}/delete`,
    Update: (id) => `/api/v1/forms/${id}/update/`,
    Hide: (id) => `/api/v1/forms/${id}/hide/`,
    Show: (id) => `/api/v1/forms/${id}/show/`
};
