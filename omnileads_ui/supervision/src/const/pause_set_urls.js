export default {
    List: '/api/v1/pause_sets',
    Create: '/api/v1/pause_sets/create/',
    Detail: (id) => `/api/v1/pause_sets/${id}`,
    Update: (id) => `/api/v1/pause_sets/${id}/update/`,
    Delete: (id) => `/api/v1/pause_sets/${id}/delete`,
    ActivePauses: '/api/v1/pause_sets/pause_options',
    PauseConfigCreate: '/api/v1/pause_config/create/',
    PauseConfigUpdate: (id) => `/api/v1/pause_config/${id}/update/`,
    PauseConfigDelete: (id) => `/api/v1/pause_config/${id}/delete`
};
