export default {
    ExternalSystemsList: '/api/v1/external_systems',
    ExternalSystemsCreate: '/api/v1/external_systems/create/',
    ExternalSystemsDetail: (id) => `/api/v1/external_systems/${id}`,
    ExternalSystemsUpdate: (id) => `/api/v1/external_systems/${id}/update/`,
    AgentsExternalSystemList: '/api/v1/agents_external_system'
};
