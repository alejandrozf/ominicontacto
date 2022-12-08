export default {
    List: '/api/v1/call_dispositions',
    Create: '/api/v1/call_dispositions/create/',
    Detail: (id) => `/api/v1/call_dispositions/${id}`,
    Update: (id) => `/api/v1/call_dispositions/${id}/update/`,
    Delete: (id) => `/api/v1/call_dispositions/${id}/delete`
};
