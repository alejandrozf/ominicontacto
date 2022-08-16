export default {
    List: '/api/v1/pauses',
    Create: '/api/v1/pauses/create/',
    Reactivate: (id) => `/api/v1/pauses/${id}/reactivate/`,
    Delete: (id) => `/api/v1/pauses/${id}/delete`,
    Update: (id) => `/api/v1/pauses/${id}/update/`,
    Detail: (id) => `/api/v1/pauses/${id}`
};
