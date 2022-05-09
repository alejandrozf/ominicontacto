export default {
    CallDispositionsList: '/api/v1/call_dispositions',
    CallDispositionsCreate: '/api/v1/call_dispositions/create/',
    CallDispositionsDetail: (id) => `/api/v1/call_dispositions/${id}`,
    CallDispositionsUpdate: (id) => `/api/v1/call_dispositions/${id}/update/`,
    CallDispositionsDelete: (id) => `/api/v1/call_dispositions/${id}/delete`
};
