export default {
    List: '/api/v1/external_site_authentications',
    Create: '/api/v1/external_site_authentications/create/',
    Test: '/api/v1/external_site_authentications/test/',
    Detail: (id) => `/api/v1/external_site_authentications/${id}`,
    Update: (id) => `/api/v1/external_site_authentications/${id}/update/`,
    Delete: (id) => `/api/v1/external_site_authentications/${id}/delete`
};
