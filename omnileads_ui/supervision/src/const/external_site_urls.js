export default {
    ExternalSitesList: '/api/v1/external_sites',
    ExternalSitesCreate: '/api/v1/external_sites/create/',
    ExternalSitesDetail: (id) => `/api/v1/external_sites/${id}`,
    ExternalSitesUpdate: (id) => `/api/v1/external_sites/${id}/update/`,
    ExternalSitesDelete: (id) => `/api/v1/external_sites/${id}/delete`,
    ExternalSitesHide: (id) => `/api/v1/external_sites/${id}/hide/`,
    ExternalSitesShow: (id) => `/api/v1/external_sites/${id}/show/`
};
