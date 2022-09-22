export default {
    List: '/api/v1/group_of_hours',
    Create: '/api/v1/group_of_hours/create/',
    Detail: (id) => `/api/v1/group_of_hours/${id}`,
    Delete: (id) => `/api/v1/group_of_hours/${id}/delete`,
    Update: (id) => `/api/v1/group_of_hours/${id}/update/`
};
