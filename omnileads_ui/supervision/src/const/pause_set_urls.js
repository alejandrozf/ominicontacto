export default {
    ActivePauses: '/api/v1/pauses',
    PauseSetsList: '/api/v1/pause_sets',
    PauseSetCreate: '/api/v1/pause_sets/create/',
    PauseSetDetail: (id) => `/api/v1/pause_sets/${id}`,
    PauseSetUpdate: (id) => `/api/v1/pause_sets/${id}/update/`,
    PauseSetDelete: (id) => `/api/v1/pause_sets/${id}/delete`,
    PauseConfigCreate: '/api/v1/pause_config/create/',
    PauseConfigUpdate: (id) => `/api/v1/pause_config/${id}/update/`,
    PauseConfigDelete: (id) => `/api/v1/pause_config/${id}/delete`
};
