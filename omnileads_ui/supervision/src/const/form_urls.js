export default {
    FormList: '/api/v1/forms',
    FormCreate: '/api/v1/forms/create/',
    FormDetail: (id) => `/api/v1/forms/${id}`,
    FormDelete: (id) => `/api/v1/forms/${id}/delete`,
    FormUpdate: (id) => `/api/v1/forms/${id}/update/`,
    FormHide: (id) => `/api/v1/forms/${id}/hide/`,
    FormShow: (id) => `/api/v1/forms/${id}/show/`
};
