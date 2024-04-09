export default {
    List: '/api/v1/external_systems',
    Create: '/api/v1/external_systems/create/',
    Detail: (id) => `/api/v1/external_systems/${id}`,
    Update: (id) => `/api/v1/external_systems/${id}/update/`,
    Delete: (id) => `/api/v1/external_systems/${id}/delete`,
    AgentsExternalSystemList: '/api/v1/agents_external_system'
};
